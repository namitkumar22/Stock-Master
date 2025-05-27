import streamlit as st
import pandas as pd
from fetchNSEdata import fetch_all_nse_symbols, fetch_nse_live_data
import pickle
import time
import threading
import os

# Page config with custom styling
st.set_page_config(
    page_title="NSE Stock Predictor", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful animations and styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto:wght@300;400;500&display=swap');

.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
    animation: headerGlow 3s ease-in-out infinite alternate;
}

@keyframes headerGlow {
    from { box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3); }
    to { box-shadow: 0 20px 60px rgba(118, 75, 162, 0.5); }
}

.main-title {
    font-family: 'Orbitron', monospace;
    font-size: 3rem;
    font-weight: 900;
    color: white;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    margin: 0;
    animation: titlePulse 2s ease-in-out infinite alternate;
}

@keyframes titlePulse {
    from { transform: scale(1); }
    to { transform: scale(1.02); }
}

.subtitle {
    font-family: 'Roboto', sans-serif;
    color: rgba(255,255,255,0.9);
    font-size: 1.2rem;
    margin-top: 0.5rem;
}

.metric-card {
    background: linear-gradient(145deg, #1e3c72, #2a5298);
    padding: 1.5rem;
    border-radius: 15px;
    margin: 1rem 0;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    border: 1px solid rgba(255,255,255,0.1);
    animation: cardFloat 4s ease-in-out infinite;
}

@keyframes cardFloat {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-5px) rotate(0.5deg); }
}

.data-section {
    background: linear-gradient(145deg, #f6f9fc, #ffffff);
    padding: 2rem;
    border-radius: 20px;
    margin: 1rem 0;
    box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    border: 1px solid rgba(102, 126, 234, 0.1);
    position: relative;
    overflow: hidden;
}

.data-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
    animation: shimmer 3s infinite;
}

@keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
}

.section-title {
    font-family: 'Orbitron', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #4CAF50;
    animation: pulse 2s infinite;
    display: inline-block;
    margin-left: 0.5rem;
}

@keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(76, 175, 80, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }
}

.loading-spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(102, 126, 234, 0.3);
    border-radius: 50%;
    border-top-color: #667eea;
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.profit-highlight {
    background: linear-gradient(135deg, #11998e, #38ef7d);
    color: white;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-weight: bold;
    animation: profitGlow 2s ease-in-out infinite alternate;
}

@keyframes profitGlow {
    from { box-shadow: 0 0 10px rgba(56, 239, 125, 0.5); }
    to { box-shadow: 0 0 20px rgba(17, 153, 142, 0.8); }
}

/* Custom dataframe styling */
.stDataFrame {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.info-message {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    animation: infoFade 2s ease-in-out infinite alternate;
}

@keyframes infoFade {
    from { opacity: 0.8; }
    to { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

def fetch_data_to_csv():
    symbols = fetch_all_nse_symbols()
    fetch_nse_live_data(symbols[:500])

def predict_profit_and_tell_best_stock():
    try:
        df = pd.read_csv("nse_live.csv")
        df = df.dropna()
        
        model = pickle.load(open("profit_prediction_model.pkl", "rb"))
        df['PREDICTED_PROFIT'] = model.predict(df[['OPEN', 'HIGH', 'LOW', 'PREVCLOSE', 'LAST']])
        
        df.to_csv("nse_live_with_profit.csv", index=False, mode='w')
        return df
    except Exception as e:
        st.error(f"Error in prediction: {e}")
        return None

def run_background_process():
    while True:
        threading.Thread(target=fetch_data_to_csv).start()
        threading.Thread(target=predict_profit_and_tell_best_stock).start()
        time.sleep(10)

# Start background process
if 'background_started' not in st.session_state:
    st.session_state.background_started = True
    threading.Thread(target=run_background_process, daemon=True).start()

# Beautiful Header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">⚡ NSE STOCK PREDICTOR ⚡</h1>
    <p class="subtitle">Real-time Market Analysis & AI-Powered Profit Predictions</p>
</div>
""", unsafe_allow_html=True)

# Status indicators
col_status1, col_status2, col_status3 = st.columns(3)

with col_status1:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: white; margin: 0;">🔄 Data Fetching</h3>
        <p style="color: rgba(255,255,255,0.8); margin: 0;">Live Updates<span class="status-indicator"></span></p>
    </div>
    """, unsafe_allow_html=True)

with col_status2:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: white; margin: 0;">🤖 AI Engine</h3>
        <p style="color: rgba(255,255,255,0.8); margin: 0;">Predicting<span class="status-indicator"></span></p>
    </div>
    """, unsafe_allow_html=True)

with col_status3:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: white; margin: 0;">📊 Analysis</h3>
        <p style="color: rgba(255,255,255,0.8); margin: 0;">Real-time<span class="status-indicator"></span></p>
    </div>
    """, unsafe_allow_html=True)

# Main content sections
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="data-section">
        <h2 class="section-title">📈 Live NSE Market Data</h2>
    """, unsafe_allow_html=True)
    
    if os.path.exists("nse_live.csv"):
        try:
            live_data = pd.read_csv("nse_live.csv")
            st.dataframe(live_data, use_container_width=True, height=400)
        except:
            st.markdown('<div class="info-message"><span class="loading-spinner"></span> Loading live market data...</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-message"><span class="loading-spinner"></span> Fetching initial market data...</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="data-section">
        <h2 class="section-title">🎯 Top 3 AI Predicted Winners</h2>
    """, unsafe_allow_html=True)
    
    if os.path.exists("nse_live_with_profit.csv"):
        try:
            profit_data = pd.read_csv("nse_live_with_profit.csv")
            top_3 = profit_data.nlargest(3, 'PREDICTED_PROFIT')
            
            # Style the profit column
            styled_df = top_3[['SYMBOL', 'LAST', 'PREDICTED_PROFIT']].copy()
            styled_df['PREDICTED_PROFIT'] = styled_df['PREDICTED_PROFIT'].round(2)
            
            st.dataframe(styled_df, use_container_width=True, height=400)
            
            # Show top prediction as highlight
            if not top_3.empty:
                top_stock = top_3.iloc[0]
                st.markdown(f"""
                <div style="text-align: center; margin-top: 1rem;">
                    <span class="profit-highlight">
                        🏆 Best Pick: {top_stock['SYMBOL']} - Predicted Profit: {top_stock['PREDICTED_PROFIT']:.2f}
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
        except:
            st.markdown('<div class="info-message"><span class="loading-spinner"></span> AI is calculating predictions...</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-message"><span class="loading-spinner"></span> Waiting for AI predictions...</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer with update info
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding: 1rem; 
           background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); 
           border-radius: 10px;">
    <p style="color: #667eea; font-weight: 500;">
        🔄 Auto-refreshing every 3 minute | 🤖 AI predictions updated every 10 seconds
    </p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh every 5 seconds
time.sleep(5)
st.rerun()