import re
from typing import TypedDict, List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

#Load API Key
import os
from dotenv import load_dotenv
load_dotenv()


# 1. Application Global State
class AgentState(TypedDict):
    ticker: str
    risk_level: str
    fav_sectors: str
    raw_api_data: Dict[str, Any]
    research_report: str
    verification_passed: bool
    pending_questions: List[str]
    user_answers: List[str]
    user_profile: Dict[str, str]  # Carries first name, last name, email to check for PII leaks

# 2. Structured Verification Contract Schema
class VerificationResult(BaseModel):
    status: str = Field(description="Must be 'PASSED' or 'FAILED'")
    questions: List[str] = Field(description="A list of 1 to 3 clarification questions if FAILED, otherwise empty.")

# 3. Research Node
def research_agent_node(state: AgentState) -> Dict[str, Any]:
    #llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.2)
    ticker = state["ticker"]
    raw_data = state.get("raw_api_data", {})
    
    prompt = f"""
    You are an expert Financial Research Agent. Analyze this raw market snapshot for ticker {ticker}:
    {raw_data}
    
    Incorporate user parameters where contextually appropriate:
    Risk Profile: {state['risk_level']}
    Favorite Sectors: {state['fav_sectors']}
    
    Compile a formal, comprehensive Markdown summary analyzing recent historical performance, valuation metrics, and risks.
    """
    
    response = llm.invoke([
        SystemMessage(content="You are a strict financial analyst. Base summaries strictly on numeric data provided. Do not hallucinate metrics."),
        HumanMessage(content=prompt)
    ])
    
    return {"research_report": response.content}

# 4. Node 2: Verification Agent (With Bulletproof Report Type Checking)
def verification_agent_node(state: AgentState) -> Dict[str, Any]:
    if state.get("user_answers"):
        return {
            "verification_passed": True,
            "pending_questions": []
        }
        
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.2)
    
    # --- SAFE REPORT NORMALIZATION ---
    report = state.get("research_report", "")
    if isinstance(report, list):
        # If it arrived as a list of messages or strings, join them together
        report = "\n".join([str(item.content if hasattr(item, 'content') else item) for item in report])
    else:
        report = str(report)
    # ---------------------------------
        
    profile = state.get("user_profile", {})
    
    # Safe Guardrail Wrapper check for PII Leakage
    pii_elements = [profile.get("first_name"), profile.get("last_name"), profile.get("email")]
    for pii in pii_elements:
        if pii and isinstance(pii, str) and pii.lower() in report.lower():
            report = re.sub(re.escape(pii), "[REDACTED_PII]", report, flags=re.IGNORECASE)
            
    prompt = f"""
    You are a high-level Financial Verification Quality Control Agent. 
    Review this report against the source API numeric data to identify inaccuracies, discrepancies, or symbol confusion.
    
    Source Data: {state['raw_api_data']}
    Generated Report: {report}
    
    If the text correctly represents the metrics, return 'PASSED'.
    If metrics look ambiguous or mismatch the raw values, flag 'FAILED' and generate 1 to 3 highly distinct clarification questions for the user.
    """
    
    structured_llm = llm.with_structured_output(VerificationResult)
    result = structured_llm.invoke([HumanMessage(content=prompt)])
    
    passed = result.status == "PASSED" or len(result.questions) == 0
    
    return {
        "research_report": report,
        "verification_passed": passed,
        "pending_questions": result.questions
    }
def route_after_verification(state: AgentState):
    if state["verification_passed"]:
        return END
    return "human_input_wait"

def human_input_placeholder(state: AgentState) -> Dict[str, Any]:
    return {}

# 5. Build Graph Workflow Definition
def build_workflow():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("researcher", research_agent_node)
    workflow.add_node("verifier", verification_agent_node)
    workflow.add_node("human_input_wait", human_input_placeholder)
    
    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "verifier")
    
    workflow.add_conditional_edges(
        "verifier",
        route_after_verification,
        {
            END: END,
            "human_input_wait": "human_input_wait"
        }
    )
    
    workflow.add_edge("human_input_wait", "verifier")
    
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory, interrupt_before=["human_input_wait"])