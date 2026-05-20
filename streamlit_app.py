import streamlit as st
import google.generativeai as genai
from PIL import Image

# ----------------------------------------------------
# 1. UI Configuration
# ----------------------------------------------------
st.set_page_config(page_title="AI Vision Analyst", layout="wide")
st.title("AI Vision-Based Chart Analyst (Free Tier)")
st.markdown("Upload a screenshot of any trading chart for instant visual structure analysis.")

# ----------------------------------------------------
# 2. Sidebar Configuration
# ----------------------------------------------------
st.sidebar.header("Configuration Panel")
gemini_key = st.sidebar.text_input("Enter Free Gemini API Key", type="password")

trading_style = st.sidebar.selectbox(
    "Your Trading Profile", 
    ["Scalper (M1-M15)", "Day Trader (M15-H1)", "Swing Trader (H4-Daily)"]
)

if not gemini_key:
    st.sidebar.warning("⚠️ Enter your Gemini API key to activate the visual scanner.")

# ----------------------------------------------------
# 3. Core Application Layout
# ----------------------------------------------------
uploaded_chart = st.file_uploader("Choose a chart screenshot...", type=["jpg", "jpeg", "png"])

if uploaded_chart is not None:
    layout_left, layout_right = st.columns([1, 1])
    
    with layout_left:
        st.subheader("Uploaded Price Action Chart")
        
        # Open image using PIL for Gemini
        img = Image.open(uploaded_chart)
        st.image(img, use_container_width=True)
        
    with layout_right:
        st.subheader("AI Structural Analysis Matrix")
        
        if st.button("Run Visual Scan", type="primary"):
            if not gemini_key:
                st.error("Please add your Gemini API Key in the sidebar.")
            else:
                with st.spinner("Scanning chart structure..."):
                    try:
                        # Configure Google Gemini
                        genai.configure(api_key=gemini_key)
                        
                        # We use gemini-1.5-flash as it is fast, highly capable in vision, and free
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        
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
                        
                        # Pass both the text prompt and the image to the model
                        response = model.generate_content([vision_prompt, img])
                        
                        st.markdown("---")
                        st.markdown(response.text)
                        
                    except Exception as e:
                        st.error(f"Vision Scanning Error: {str(e)}")
