import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from openai import OpenAI

# ----------------------------------------------------
# 1. UI & Interface Setup
# ----------------------------------------------------
st.set_page_config(page_title="BullGPT Engine", layout="wide", page_icon="🐂")
st.title("🐂 BullGPT Execution Engine")
st.markdown("Automated technical analysis and quantitative limit-order matrices.")

# ----------------------------------------------------
# 2. Sidebar Configuration (Pro Mode)
# ----------------------------------------------------
st.sidebar.header("API & Market Routing")
openai_key = st.sidebar.text_input("OpenAI API Key", type="password")

# Pre-loaded for high-volatility markets
market_choices = {
    "Gold (XAU/USD)": "GC=F",
    "Silver (XAG/USD)": "SI=F",
    "Bitcoin (BTC/USD)": "BTC-USD"
}
selected_market = st.sidebar.selectbox("Select Asset", list(market_choices.keys()))
ticker = market_choices[selected_market]

# Granular intraday timeframes
interval = st.sidebar.selectbox("Timeframe", ["5m", "15m", "1h"], index=1)
period = "5d" if interval in ["5m", "15m"] else "1mo"

# ----------------------------------------------------
# 3. Data Extraction & Processing
# ----------------------------------------------------
def pull_market_data(t, i, p):
    df = yf.Ticker(t).history(period=p, interval=i)
    if df.empty: 
        return None, None
        
    # Calculate RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df, df.iloc[-1]

if ticker:
    df, latest = pull_market_data(ticker, interval, period)
    
    if latest is not None:
        price = latest['Close']
        rsi = latest['RSI']
        
        # Display live metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", f"${price:.2f}")
        col2.metric("RSI (14)", f"{rsi:.2f}")
        col3.metric("Interval", interval.upper())
        
        layout_l, layout_r = st.columns([1.2, 1])
        
        # Professional Candlestick Chartting
        with layout_l:
            fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'], name="Price Action")])
            
            fig.update_layout(
                template="plotly_dark", 
                margin=dict(l=0, r=0, t=30, b=0), 
                height=450,
                xaxis_rangeslider_visible=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
        # AI Order Flow Generation
        with layout_r:
            st.subheader("AI Order Flow Analysis")
            if st.button("Generate Trade Setup", type="primary"):
                if not openai_key:
                    st.error("⚠️ API Key required in the sidebar.")
                else:
                    with st.spinner("Analyzing price action and volume..."):
                        try:
                            client = OpenAI(api_key=openai_key)
                            
                            # Advanced prompt targeting limits and No SD zones
                            prompt = f"""
                            Analyze the current market structure for {selected_market} on the {interval} timeframe.
                            Current Price: ${price:.2f}
                            RSI: {rsi:.2f}
                            
                            Provide a strict, execution-focused trading setup including:
                            1. Specific Buy Limit or Sell Limit order coordinates based on recent retracements.
                            2. Exact Stop-Loss and Take-Profit zones.
                            3. Evaluate the price action to confirm if a 'No SD' (No Supply / No Demand) setup is present.
                            
                            Output in a highly structured, institutional format. Do not use generic warnings.
                            """
                            
                            res = client.chat.completions.create(
                                model="gpt-4o",
                                messages=[
                                    {"role": "system", "content": "You are an elite quantitative trader who speaks in precise execution parameters."},
                                    {"role": "user", "content": prompt}
                                ],
                                temperature=0.4
                            )
                            st.markdown("---")
                            st.markdown(res.choices[0].message.content)
                        except Exception as e:
                            st.error(f"API Error: {str(e)}")