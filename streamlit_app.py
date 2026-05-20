import streamlit as st
import google.generativeai as genai
from PIL import Image

# ----------------------------------------------------
# 1. INITIAL CONFIGURATION
# ----------------------------------------------------
st.set_page_config(page_title="AI Vision Analyst", layout="wide")

# ----------------------------------------------------
# 2. ACCESS KEY LOGIN SYSTEM
# ----------------------------------------------------
def check_access():
    """Checks if the user has entered a valid access key."""
    if "access_granted" not in st.session_state:
        st.session_state["access_granted"] = False

    if not st.session_state["access_granted"]:
        st.title("🔐 Welcome to BullGPT Analyst")
        st.markdown("Please enter your private access key to use the scanner.")
        
        user_key = st.text_input("Access Key", type="password")
        
        if st.button("Login"):
            # Check if the entered key is in our secret list of valid keys
            if user_key in st.secrets["valid_access_keys"]:
                st.session_state["access_granted"] = True
                st.rerun()
            else:
                st.error("🚫 Invalid or expired access key.")
        return False
    return True

# ----------------------------------------------------
# 3. MAIN APPLICATION (Only runs if unlocked)
# ----------------------------------------------------
if check_access():
    
    st.title("📊 AI Vision-Based Chart Analyst")
    st.markdown("Upload a screenshot of any trading chart for instant visual structure analysis.")

    # Sidebar Configuration (No longer asks for API Key!)
    st.sidebar.header("Configuration Panel")
    
    trading_style = st.sidebar.selectbox(
        "Your Trading Profile", 
        ["Scalper (M1-M15)", "Day Trader (M15-H1)", "Swing Trader (H4-Daily)"]
    )
    
    if st.sidebar.button("Log Out"):
        st.session_state["access_granted"] = False
        st.rerun()

    # Core Application Layout
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
                        # PULL THE API KEY DIRECTLY FROM HIDDEN SECRETS
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
