import streamlit as st
import google.generativeai as genai
from PIL import Image

# ----------------------------------------------------
# 1. UI & CSS OVERHAUL
# ----------------------------------------------------
st.set_page_config(page_title="AI Trading Analyst", layout="wide", initial_sidebar_state="collapsed")

# Inject Custom CSS for Dark Theme & SaaS look
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #ffffff; }
    .stButton>button {
        background-color: #00d06b; color: black; border-radius: 8px; border: none;
        padding: 0.75rem 1.5rem; font-weight: 800; width: 100%; transition: all 0.3s ease;
    }
    .stButton>button:hover { background-color: #00ff84; box-shadow: 0 0 15px rgba(0, 208, 107, 0.4); }
    header {visibility: hidden;} footer {visibility: hidden;}
    .stTextInput input { background-color: #1a1a1a; color: white; border: 1px solid #333; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. THE "LANDING PAGE" & ACCESS KEY SYSTEM
# ----------------------------------------------------
def auth_system():
    if "access_granted" not in st.session_state:
        st.session_state["access_granted"] = False

    if not st.session_state["access_granted"]:
        
        # --- HERO SECTION ---
        st.markdown("<h1 style='text-align: center; font-size: 3rem;'>Get pro-level analysis instantly with AI.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888; font-size: 1.2rem;'>Upload a chart and get institutional-grade support, resistance, and execution scenarios in 5 seconds.</p>", unsafe_allow_html=True)
        st.write("")
        st.write("")
        
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            st.markdown("<h3 style='text-align: center;'>Enter Invite Key</h3>", unsafe_allow_html=True)
            user_key = st.text_input("Access Key", type="password", label_visibility="collapsed")
            
            if st.button("Unlock Scanner", type="primary"):
                # Check against the keys in your Streamlit Secrets
                if user_key in st.secrets["valid_keys"]:
                    st.session_state["access_granted"] = True
                    st.rerun()
                else:
                    st.error("🚫 Invalid or expired access key.")

        st.write("---")
        
        # --- HOW IT WORKS SECTION ---
        st.markdown("<h2 style='text-align: center;'>How it works</h2>", unsafe_allow_html=True)
        st.write("")
        step1, step2, step3 = st.columns(3)
        with step1:
            st.subheader("1. Take a screenshot")
            st.write("Snap a screenshot of your M5, M15, or H1 chart.")
        with step2:
            st.subheader("2. AI Analysis")
            st.write("Our engine scans for No SD zones, liquidity sweeps, and limits.")
        with step3:
            st.subheader("3. Execute")
            st.write("Get strict bull/bear scenarios with exact invalidation levels.")
            
        return False
    return True

# ----------------------------------------------------
# 3. THE APP DASHBOARD (Only visible when unlocked)
# ----------------------------------------------------
if auth_system():
    
    st.title("⚡ AI Execution Matrix")
    
    with st.sidebar:
        st.header("Terminal Settings")
        trading_style = st.selectbox("Trading Style", ["Scalper (M1-M15)", "Day Trader (M15-H1)", "Swing (H4+)"])
        st.write("---")
        if st.button("Lock System"):
            st.session_state["access_granted"] = False
            st.rerun()

    uploaded_chart = st.file_uploader("Upload Chart Screenshot", type=["jpg", "jpeg", "png"])

    if uploaded_chart is not None:
        layout_left, layout_right = st.columns([1, 1])
        
        with layout_left:
            img = Image.open(uploaded_chart)
            st.image(img, use_container_width=True)
            
        with layout_right:
            st.subheader("Structural Analysis")
            
            if st.button("Generate Setup", type="primary"):
                with st.spinner("Calculating matrices..."):
                    try:
                        # Pull your private Gemini key from Streamlit Secrets
                        my_hidden_key = st.secrets["gemini_api_key"]
                        genai.configure(api_key=my_hidden_key)
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        
                        vision_prompt = f"""
                        You are an elite discretionary price action trader. Analyze this chart for a {trading_style} profile. 
                        Provide:
                        1. **Market Structure:** Trend bias.
                        2. **Liquidity Levels:** Major support/resistance or Supply/Demand zones. 
                        3. **Execution Scenarios:**
                           - **Bull Case:** Entry, target, invalidation.
                           - **Bear Case:** Entry, target, invalidation.
                        4. **Score:** Setup quality (1-10).
                        Output plain text only. Be highly precise.
                        """
                        
                        response = model.generate_content([vision_prompt, img])
                        st.markdown(response.text)
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
