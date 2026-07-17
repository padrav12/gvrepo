import streamlit as st
import sqlite3
import hashlib
import datetime
import yfinance as yf
import plotly.graph_objects as go
from app_graph import build_workflow

# --- Custom Professional Theme CSS Injection ---
# --- Custom Professional Light Theme CSS Injection ---
def inject_professional_styling():
    st.markdown(
        """
        <style>
        /* Global Background & Light Base Theme */
        .main {
            background-color: #F8FAFC !important; /* Soft White/Slate-tint Background */
            color: #0F172A !important;           /* Dark Slate Text */
        }
        
        /* Light Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #F1F5F9 !important; /* Light Slate Gray Sidebar */
            border-right: 1px solid #CBD5E1;
        }
        
        /* Professional Green Titles & Accent Headers */
        h1, h2, h3, h4 {
            color: #047857 !important; /* Rich Professional Emerald Green */
            font-family: 'Inter', sans-serif;
            font-weight: 700;
        }
        
        /* Styled Input Cards (Light Accent) */
        div[data-testid="stForm"], div.stTextInput, div.stSelectbox, div.stDateInput {
            background-color: #FFFFFF !important;
            border-radius: 8px;
            padding: 2px;
        }
        
        /* Buttons styling: Emerald Green with crisp text */
        div.stButton > button {
            background-color: #10B981 !important; /* Solid Emerald Green */
            color: #FFFFFF !important;
            border: 1px solid #059669 !important;
            border-radius: 6px !important;
            padding: 0.5rem 1.5rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            background-color: #059669 !important; /* Deeper Forest Green on Hover */
            box-shadow: 0px 4px 12px rgba(16, 185, 129, 0.2);
            transform: translateY(-1px);
        }
        
        /* Alerts & Info Blocks (Soft Green Tints) */
        div.stAlert {
            background-color: #ECFDF5 !important; /* Very soft pastel mint background */
            border-left: 5px solid #10B981 !important;
            border-radius: 6px;
            color: #065F46 !important;
        }
        
        /* Metrics Card Customizations */
        div[data-testid="stMetricValue"] {
            color: #047857 !important; /* Deep Green for clean numbers readability */
            font-weight: 800;
        }
        div[data-testid="stMetricLabel"] {
            color: #475569 !important; /* Medium Slate Gray for subtext labels */
        }
        
        /* Footer/Disclaimer Light styling */
        .disclaimer-box {
            background-color: #F1F5F9;
            border: 1px solid #E2E8F0;
            padding: 15px;
            border-radius: 8px;
            margin-top: 30px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
# --- Required Global Disclaimer Caption Function ---
def display_global_disclaimer():
    st.markdown("---")
    st.markdown(
        """
        <div class="disclaimer-box">
            <p style="font-size:0.8rem; color:#94A3B8; margin:0; line-height:1.5;">
                <strong>Disclaimer:</strong> This site is displaying data from online portals and there is no guarantee of the data accuracy. 
                This is just a project developed to improve personal capability in Agentic AI. Also Investments 
                have to be done at your own risk and you shouldn't follow the above displayed data to buy or sell stocks. 
                Please login to authorized investment portals to capture the most accurate data to make investments decisions. 
                We are not responsible for any right or wrong investment decisions made from above data.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Persistent Text Logging Utilities ---
# --- Enhanced Persistent Text Logging Utilities ---
def log_auth_event(userid: str, status: str, first_name: str = "N/A", last_name: str = "N/A"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_name = f"{first_name} {last_name}".strip()
    
    with open("auth_logs.txt", "a") as f:
        f.write(f"[{timestamp}] UserID: '{userid}' | Name: '{full_name}' | Login Status: {status}\n")

# --- Database Core Setup ---
def init_db():
    conn = sqlite3.connect("gviz_users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    userid TEXT PRIMARY KEY, 
                    password TEXT, 
                    first_name TEXT, 
                    last_name TEXT, 
                    country TEXT, 
                    state TEXT, 
                    city TEXT, 
                    email TEXT,
                    risk_level TEXT,
                    fav_sectors TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Page Configurations
st.set_page_config(page_title="GVIZ Financial Information", layout="wide")
inject_professional_styling()

# Session State Keys Init
if "auth_state" not in st.session_state:
    st.session_state.auth_state = "login"
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# ---------------------------------------------------------
# AUTHENTICATION ROUTER INTERFACES
# ---------------------------------------------------------

if st.session_state.auth_state != "authenticated":
    st.title("Welcome to GVIZ Financial Information")
    
    # Render styled sign-in/register wrapper container
    with st.container():
        # --- OPTION A: LOGIN GATE ---
        if st.session_state.auth_state == "login":
            st.subheader("🔒 Professional Client Access")
            
            col_u, col_p = st.columns(2)
            with col_u:
                login_uid = st.text_input("User ID")
            with col_p:
                login_pwd = st.text_input("Password", type="password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1.5, 1.5, 2])
            with col1:
                if st.button("Sign In Securely"):
                    hashed_pwd = hashlib.sha256(login_pwd.encode()).hexdigest()
                    conn = sqlite3.connect("gviz_users.db")
                    c = conn.cursor()
                    c.execute("SELECT * FROM users WHERE userid=? AND password=?", (login_uid, hashed_pwd))
                    user_row = c.fetchone()
                    conn.close()
                    
                    if user_row:
                        st.session_state.auth_state = "authenticated"
                        st.session_state.user_data = {
                            "userid": user_row[0], "first_name": user_row[2], "last_name": user_row[3],
                            "country": user_row[4], "city": user_row[6], "email": user_row[7],
                            "risk_level": user_row[8], "fav_sectors": user_row[9]
                        }
                        # SUCCESS LOG: Capture real database tracking structures
                        log_auth_event(
                            userid=user_row[0], 
                            status="SUCCESSFUL", 
                            first_name=user_row[2], 
                            last_name=user_row[3]
                        )
                        st.rerun()
                    else:
                        st.error("Invalid User ID or Password combination.")
                        # FAILED LOG: Name values aren't known for invalid attempts
                        log_auth_event(userid=login_uid, status="FAILED", first_name="Unknown", last_name="Attempt")
            with col2:
                if st.button("Create Account"):
                    st.session_state.auth_state = "register"
                    st.rerun()
            with col3:
                if st.button("Password Reset Help"):
                    st.session_state.auth_state = "forgot"
                    st.rerun()

        # --- OPTION B: REGISTER ---
        elif st.session_state.auth_state == "register":
            st.subheader("📝 Open an Account")
            
            c_u, c_p = st.columns(2)
            with c_u:
                reg_uid = st.text_input("User ID")
            with c_p:
                reg_pwd = st.text_input("Password", type="password")
                
            c_fn, c_ln = st.columns(2)
            with c_fn:
                reg_fn = st.text_input("First Name")
            with c_ln:
                reg_ln = st.text_input("Last Name")
                
            reg_email = st.text_input("Email Address")
            
            c_co, c_st, c_ci = st.columns(3)
            with c_co:
                reg_country = st.selectbox("Country", ["United States", "India"])
            with c_st:
                reg_state = st.text_input("State")
            with c_ci:
                reg_city = st.text_input("City")
            
            st.markdown("#### Preferences Config")
            c_r, c_s = st.columns(2)
            with c_r:
                reg_risk = st.selectbox("Risk Level Profile", ["Low", "Moderate", "High"])
            with c_s:
                reg_sectors = st.text_input("Favorite Sectors", value="Technology")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Submit Registration Details"):
                if reg_uid and reg_pwd and reg_fn and reg_ln and reg_email and reg_city:
                    hashed_pwd = hashlib.sha256(reg_pwd.encode()).hexdigest()
                    try:
                        conn = sqlite3.connect("gviz_users.db")
                        c = conn.cursor()
                        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                  (reg_uid, hashed_pwd, reg_fn, reg_ln, reg_country, reg_state, reg_city, reg_email, reg_risk, reg_sectors))
                        conn.commit()
                        conn.close()
                        st.success("Account successfully provisioned! Returning to login panel...")
                        st.session_state.auth_state = "login"
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("This User ID is already registered.")
                else:
                    st.error("Please fill in all requested identification values.")
                    
            if st.button("Back to Login"):
                st.session_state.auth_state = "login"
                st.rerun()

        # --- OPTION C: FORGOT PASSWORD ---
        elif st.session_state.auth_state == "forgot":
            st.subheader("🔑 Secure Password Recovery")
            f_uid = st.text_input("Confirm User ID")
            f_email = st.text_input("Confirm Email ID")
            f_city = st.text_input("Confirm City")
            f_new_pwd = st.text_input("Specify New Password", type="password")
            
            if st.button("Reset Password"):
                conn = sqlite3.connect("gviz_users.db")
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE userid=? AND email=? AND city=?", (f_uid, f_email, f_city))
                record = c.fetchone()
                
                if record:
                    hashed_new_pwd = hashlib.sha256(f_new_pwd.encode()).hexdigest()
                    c.execute("UPDATE users SET password=? WHERE userid=?", (hashed_new_pwd, f_uid))
                    conn.commit()
                    st.success("Identity validated. Password has been securely updated.")
                    st.session_state.auth_state = "login"
                    conn.close()
                    st.rerun()
                else:
                    st.error("User validation inputs did not match our records.")
                conn.close()
                
            if st.button("Cancel"):
                st.session_state.auth_state = "login"
                st.rerun()
                
    display_global_disclaimer()
    st.stop()

# ---------------------------------------------------------
# MAIN DASHBOARD PANEL
# ---------------------------------------------------------

st.title("Welcome to GVIZ Financial Information")

# Sidebar Metrics Info Card
st.sidebar.markdown("### 👤 Session Information")
st.sidebar.markdown(f"**Operator ID:** `{st.session_state.user_data['userid']}`")
st.sidebar.markdown(f"**Risk Profile:** `{st.session_state.user_data['risk_level']}`")
st.sidebar.markdown(f"**Favorite Sectors:** `{st.session_state.user_data['fav_sectors']}`")

if st.sidebar.button("Logout Session"):
    st.session_state.auth_state = "login"
    st.session_state.user_data = {}
    st.rerun()

# Workspace Configuration Form Layout
with st.expander("🛠️ Workspace Controls & Parameters", expanded=True):
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        ticker_input = st.text_input("Stock Tickers (Comma separated)", value="AAPL, TSLA")
    with col_b:
        start_date = st.date_input("Start Window", datetime.date(2025, 1, 1))
    with col_c:
        end_date = st.date_input("End Window", datetime.date(2026, 1, 1))

    freq_interval = st.selectbox("Historical Interval Metric", ["30m", "90m", "1d", "5d", "1mo", "6mo", "1y", "5y"])

    st.markdown("**Display Properties:**")
    c1, c2, c3, c4, c5 = st.columns(5)
    f_detail = c1.checkbox("Detailed Output", value=True)
    f_price = c2.checkbox("Current Price", value=True)
    f_pe = c3.checkbox("PE Ratio", value=True)
    f_div = c4.checkbox("Dividends", value=True)
    f_mcap = c5.checkbox("Market Cap", value=True)

# Graph Engine Bindings
app = build_workflow()
thread_id = f"gviz_session_{st.session_state.user_data['userid']}"
thread_config = {"configurable": {"thread_id": thread_id}}

if st.button("Analyze Financial Query"):
    ticker_list = [t.strip().upper() for t in ticker_input.split(",")]
    
    with st.spinner("Executing real-time API integrations and chart structures..."):
        aggregated_metrics = {}
        
        for individual_ticker in ticker_list:
            ticker_obj = yf.Ticker(individual_ticker)
            info = ticker_obj.info if ticker_obj.info else {}
            
            # Simple placeholder validation mapping
            if not info or ('regularMarketPrice' in info or 'currentPrice' in info or 'shortName' in info):
                pass
            else:
                st.error(f"Guardrails Warning: Validation failure for symbol '{individual_ticker}'. Execution halted.")
                st.stop()
                
            history_dataframe = ticker_obj.history(
                start=start_date, 
                end=end_date, 
                interval=freq_interval if "m" in freq_interval or "d" in freq_interval else "1d"
            )
            
            # Conditionally populate local metric variables
            ticker_profile = {}
            if f_price: ticker_profile["Current Price"] = info.get("currentPrice", info.get("regularMarketPreviousClose", "N/A"))
            if f_pe: ticker_profile["Trailing PE Ratio"] = info.get("trailingPE", "N/A")
            if f_div: ticker_profile["Dividend Yield Rate"] = info.get("dividendYield", "N/A")
            if f_mcap: ticker_profile["Market Cap"] = info.get("marketCap", "N/A")
            if f_detail: ticker_profile["Volume Metric"] = info.get("volume", "N/A")
            
            aggregated_metrics[individual_ticker] = {
                "metrics": ticker_profile,
                "earnings_summary": f"Recent operational revenue beats or margins trended against risk threshold constraints."
            }
            
            # Clean grid columns for numerical metrics
            st.markdown(f"### 📈 Live Snapshot: {individual_ticker}")
            metric_cols = st.columns(len(ticker_profile))
            for i, (k, v) in enumerate(ticker_profile.items()):
                formatted_val = f"${v:,.2f}" if isinstance(v, (int, float)) and "Price" in k else (f"{v:,.0f}" if isinstance(v, (int, float)) and "Cap" in k else str(v))
                metric_cols[i].metric(label=k, value=formatted_val)
            
            # --- Visual Analytics Rendering (Candlestick + Performance Line) ---
            if not history_dataframe.empty:
                st.markdown(f"#### 📊 Performance Visualizations: {individual_ticker}")
                
                # Create two clean columns to display charts side-by-side or stacked cleanly
                tab1, tab2 = st.tabs(["📈 Closing Price Trend", "🕯️ Candlestick Price Action"])
                
                # --- TAB 1: NEW CLOSING PRICE PERFORMANCE LINE GRAPH ---
                with tab1:
                    fig_line = go.Figure()
                    
                    # Add a shaded area line chart
                    fig_line.add_trace(go.Scatter(
                        x=history_dataframe.index,
                        y=history_dataframe['Close'],
                        mode='lines',
                        name='Close Price',
                        line=dict(color='#047857', width=3),  # Deep Emerald Green Line
                        fill='tozeroy',                      # Shade the area under the line
                        fillcolor='rgba(16, 185, 129, 0.1)'  # Very soft green translucent tint
                    ))
                    
                    fig_line.update_layout(
                        template="plotly_white",
                        paper_bgcolor="#FFFFFF",
                        plot_bgcolor="#F8FAFC",
                        height=400,
                        margin=dict(l=40, r=40, t=20, b=40),
                        xaxis=dict(
                            showgrid=True, 
                            gridcolor="#E2E8F0", 
                            title="Timeline Window",
                            title_font=dict(color="#475569")
                        ),
                        yaxis=dict(
                            showgrid=True, 
                            gridcolor="#E2E8F0", 
                            title="Closing Price (USD)",
                            title_font=dict(color="#475569")
                        )
                    )
                    st.plotly_chart(fig_line, use_container_width=True)
                
                # --- TAB 2: ORIGINAL CANDLESTICK CHART ---
                with tab2:
                    fig_candle = go.Figure(data=[go.Candlestick(
                        x=history_dataframe.index,
                        open=history_dataframe['Open'], 
                        high=history_dataframe['High'],
                        low=history_dataframe['Low'], 
                        close=history_dataframe['Close'],
                        increasing_line_color='#10B981',  # Professional Green
                        decreasing_line_color='#EF4444'   # Professional Red
                    )])
                    
                    fig_candle.update_layout(
                        template="plotly_white",
                        paper_bgcolor="#FFFFFF",
                        plot_bgcolor="#F8FAFC",
                        height=400,
                        margin=dict(l=40, r=40, t=20, b=40),
                        xaxis=dict(
                            showgrid=True, 
                            gridcolor="#E2E8F0", 
                            title="Timeline Window",
                            title_font=dict(color="#475569")
                        ),
                        yaxis=dict(
                            showgrid=True, 
                            gridcolor="#E2E8F0", 
                            title="Price USD",
                            title_font=dict(color="#475569")
                        ),
                        xaxis_rangeslider_visible=False
                    )
                    st.plotly_chart(fig_candle, use_container_width=True)
            else:
                st.info(f"No candlestick tracking data available for symbol {individual_ticker} in this time scale.")
                
        # Invoke Graph State Lifecycle
        initial_graph_payload = {
            "ticker": ticker_input,
            "risk_level": st.session_state.user_data['risk_level'],
            "fav_sectors": st.session_state.user_data['fav_sectors'],
            "raw_api_data": aggregated_metrics,
            "research_report": "",
            "verification_passed": False,
            "pending_questions": [],
            "user_answers": [],
            "user_profile": {
                "first_name": st.session_state.user_data['first_name'],
                "last_name": st.session_state.user_data['last_name'],
                "email": st.session_state.user_data['email']
            }
        }
        
        app.invoke(initial_graph_payload, thread_config)

# --- Evaluate Running Checkpoint Thread Output Elements ---
graph_runtime_snapshot = app.get_state(thread_config)

# 1. Safely initialize runtime_values as an empty dictionary default
runtime_values = {}

if graph_runtime_snapshot and graph_runtime_snapshot.values:
    # Overwrite with the real state values if the graph has been executed
    runtime_values = graph_runtime_snapshot.values

# 2. Only attempt to parse and print if runtime_values actually contains data
if runtime_values and runtime_values.get("research_report"):
    st.markdown("---")
    st.subheader("📋 Professional Agent Summary Analysis Report")
    
    raw_report = runtime_values["research_report"]
    clean_text = ""
    
    try:
        # Check if it's a string representation of a dictionary object
        if isinstance(raw_report, str):
            stripped = raw_report.strip()
            if stripped.startswith("{") and stripped.endswith("}"):
                import ast
                parsed_dict = ast.literal_eval(stripped)
                if isinstance(parsed_dict, dict) and "text" in parsed_dict:
                    clean_text = str(parsed_dict["text"])
                else:
                    clean_text = stripped
            else:
                clean_text = raw_report
        
        elif isinstance(raw_report, dict):
            if "text" in raw_report:
                clean_text = str(raw_report["text"])
            else:
                clean_text = str(raw_report)
                
        elif isinstance(raw_report, list):
            clean_text = "\n".join([str(item.content if hasattr(item, 'content') else item) for item in raw_report])
            
        else:
            clean_text = str(raw_report)
            
    except Exception as e:
        clean_text = str(raw_report)
        
    # Render inside our styled professional light container
    st.markdown(
        f"""
        <div style="background-color: #FFFFFF; border-radius: 8px; padding: 25px; border: 1px solid #E2E8F0; color: #0F172A; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); line-height: 1.6;">
            {clean_text}
        </div>
        """, 
        unsafe_allow_html=True
    )

# 3. Only look for validation/clarification questions if runtime_values exists
if runtime_values:
    validation_queries = runtime_values.get("pending_questions", [])
    
    if validation_queries:
        st.markdown("---")
        st.warning("⚠️ Verification Agent identified ambiguous items requiring human context validation.")
        st.subheader("Clarification Requests Console")
        
        gathered_responses = []
        for index, text_query in enumerate(validation_queries):
            response_input = st.text_input(f"Question {index+1}: {text_query}", key=f"form_q_{index}")
            gathered_responses.append(response_input)
            
        if st.button("Submit Context Answers & Clear Gate"):
            if all(gathered_responses):
                app.update_state(
                    thread_config,
                    {"user_answers": gathered_responses},
                    as_node="human_input_wait"
                )
                with st.spinner("Re-executing state verification..."):
                    app.invoke(None, thread_config)
                st.rerun()
            else:
                st.error("Every pending verification prompt must be answered.")
    else:
        if runtime_values.get("verification_passed"):
            st.success("✅ Multi-Agent Workflow Complete: Cleaned, checked, and validated against standard rules.")

display_global_disclaimer()