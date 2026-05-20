import streamlit as st
import google.generativeai as genai
from PIL import Image
from supabase import create_client, Client

# ----------------------------------------------------
# 1. INITIAL CONFIGURATION
# ----------------------------------------------------
st.set_page_config(page_title="AI Vision Analyst", layout="wide")

# Initialize Supabase Client
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# ----------------------------------------------------
# 2. SUPABASE AUTHENTICATION SYSTEM
# ----------------------------------------------------
def auth_system():
    if "user_authenticated" not in st.session_state:
        st.session_state["user_authenticated"] = False

    if not st.session_state["user_authenticated"]:
        st.title("🔐 Welcome to BullGPT Analyst")
        st.markdown("Create an account or log in to access the chart scanner.")
        
        # Create Login / Register Tabs
        tab1, tab2 = st.tabs(["Log In", "Register"])
        
        with tab1:
            st.subheader("Sign In")
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", type="primary"):
                try:
                    # Send credentials to Supabase
                    response = supabase.auth.sign_in_with_password({
                        "email": login_email,
                        "password": login_password
                    })
                    st.session_state["user_authenticated"] = True
                    st.success("Logged in successfully!")
                    st.rerun()
                except Exception as e:
                    st.error("Invalid email or password.")
                    
        with tab2:
            st.subheader("Create a Free Account")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password (min 6 characters)", type="password", key="reg_password")
            
            if st.button("Register", type="primary"):
                try:
                    # Create new user in Supabase
                    response = supabase.auth.sign_up({
                        "email": reg_email,
                        "password": reg_password
                    })
                    st.success("Account created! You can now log in.")
                except Exception as e:
                    st.error(f"Registration failed: {str(e)}")
                    
        return False
    return True

# ----------------------------------------------------
# 3. MAIN APPLICATION (Only runs if authenticated)
# ----------------------------------------------------
if auth_system():
    
    st.title("📊 AI Vision-Based Chart Analyst")
    st.markdown("Upload a screenshot of any trading chart for instant visual structure analysis.")

    st.sidebar.header("Configuration Panel")
    
    trading_style = st.sidebar.selectbox(
        "Your Trading Profile", 
        ["Scalper (M1-M15)", "Day Trader (M15-H1)", "Swing Trader (H4-Daily)"]
    )
    
    # Logout Button
    if st.sidebar.button("Log Out"):
        supabase.auth.sign_out()
        st.session_state["user_authenticated"] = False
        st.rerun()

    uploaded_chart = st.file_uploader("Choose a chart screenshot...", type=["jpg", "jpeg", "png"])

    if uploaded_chart is not None:
        layout_left, layout_right = st.columns([1, 1])
        
        with layout_left:
            st.subheader("Uploaded Price Action Chart")
            img = Image.open(uploaded_chart)
            st.image(img, use_container_width=True)
            
        with layout_right:
            st.subheader("AI Structural Analysis Matrix")
            
            if st.button("Run Visual Scan", type="primary"):
                with st.spinner("Scanning chart structure..."):
                    try:
                        my_hidden_key = st.secrets["gemini_api_key"]
                        genai.configure(api_key=my_hidden_key)
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        
                        vision_prompt = f"""
                        You are an elite discretionary price action trader. Analyze this trading chart image based on a {trading_style} profile. 
                        
                        Provide a strict, professional trade setup layout covering:
                        1. **Market Structure Evaluation:** Define current trend bias.
                        2. **Key Liquidity Levels:** Identify visible major support, resistance, or Supply/Demand zones. 
                        3. **Execution Scenarios:**
                           - **Bull Case Scenario:** Potential long entry coordinates, target, and invalidation level.
                           - **Bear Case Scenario:** Potential short entry coordinates, target, and invalidation level.
                        4. **Risk Assessment Score:** Rate the quality of the visual setup from 1-10.
                        
                        Speak in absolute parameter terms. Output plain text only. Do not use generic financial disclaimers.
                        """
                        
                        response = model.generate_content([vision_prompt, img])
                        st.markdown("---")
                        st.markdown(response.text)
                        
                    except Exception as e:
                        st.error(f"Vision Scanning Error: {str(e)}")
