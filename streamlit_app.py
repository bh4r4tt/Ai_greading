import streamlit as st
from openai import OpenAI
import base64

# ----------------------------------------------------
# 1. UI Configuration
# ----------------------------------------------------
st.set_page_config(page_title="AI Vision Analyst", layout="wide", page_icon="📊")
st.title("📊 AI Vision-Based Chart Analyst")
st.markdown("Upload a screenshot of any trading chart (M5, M15, Daily) for instant visual structure analysis.")

# ----------------------------------------------------
# 2. Sidebar Configuration
# ----------------------------------------------------
st.sidebar.header("Configuration Panel")
openai_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

trading_style = st.sidebar.selectbox(
    "Your Trading Profile", 
    ["Scalper (M1-M15)", "Day Trader (M15-H1)", "Swing Trader (H4-Daily)"]
)

if not openai_key:
    st.sidebar.warning("⚠️ Enter your OpenAI API key to activate the visual scanner.")

# Helper function to convert the uploaded image to base64 for OpenAI Vision API
def encode_uploaded_image(uploaded_file):
    return base64.b64encode(uploaded_file.read()).decode('utf-8')

# ----------------------------------------------------
# 3. Core Application Layout
# ----------------------------------------------------
# File uploader optimized for iOS Photo Library / Browser uploads
uploaded_chart = st.file_uploader("Choose a chart screenshot...", type=["jpg", "jpeg", "png"])

if uploaded_chart is not None:
    # Display layout split: Left side shows your image, Right side displays AI output
    layout_left, layout_right = st.columns([1, 1])
    
    with layout_left:
        st.subheader("Uploaded Price Action Chart")
        st.image(uploaded_chart, use_container_width=True)
        
    with layout_right:
        st.subheader("AI Structural Analysis Matrix")
        
        if st.button("Run Visual Scan", type="primary"):
            if not openai_key:
                st.error("Please add your OpenAI API Key in the sidebar to execute the vision module.")
            else:
                with st.spinner("Processing chart patterns and mapping institutional liquidity zones..."):
                    try:
                        # 1. Convert image to string format
                        base64_image = encode_uploaded_image(uploaded_chart)
                        
                        # 2. Initialize OpenAI Vision Client
                        client = OpenAI(api_key=openai_key)
                        
                        # 3. Construct a highly specific prompt targeting your setup style
                        vision_prompt = f"""
                        You are an elite discretionary price action trader and quantitative analyst. 
                        Analyze this trading chart image based on a {trading_style} profile. 
                        
                        Look closely at the candle structures, support/resistance lines, volume (if visible), and technical indicators. 
                        
                        Provide a strict, professional trade setup layout covering:
                        1. **Market Structure Evaluation:** Define current trend bias (Bullish/Bearish/Consolidating) and market context.
                        2. **Key Liquidity Levels:** Identify visible major support, resistance, or Supply/Demand zones. Keep an eye out for potential 'No SD' (No Supply/No Demand) test setups or retracements.
                        3. **Execution Scenarios (Probability Matrix):**
                           - **Bull Case Scenario:** Potential long entry coordinates, target take-profit zones, invalidation level (stop-loss), and historical probability score (e.g., 65%).
                           - **Bear Case Scenario:** Potential short entry coordinates, target take-profit zones, invalidation level (stop-loss), and historical probability score.
                        4. **Risk Assessment Score:** Rate the quality of the visual setup from 1-10 based on structure clarity.
                        
                        Speak in absolute parameter terms. Do not add generic financial disclaimers or conversational fluff.
                        """
                        
                        # 4. Call GPT-4o's Vision API
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": vision_prompt},
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{base64_image}"
                                            }
                                        }
                                    ]
                                }
                            ],
                            max_tokens=1000,
                            temperature=0.3  # Kept low for deterministic, strict technical matching
                        )
                        
                        st.markdown("---")
                        st.markdown(response.choices[0].message.content)
                        
                    except Exception as e:
                        st.error(f"Vision Scanning Error: {str(e)}")
