import streamlit as st
import pandas as pd
from fetchNSEdata import fetch_all_nse_symbols, fetch_nse_live_data
import pickle
import time
import threading
import os
import logging
from datetime import datetime, timedelta
import queue
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nse_predictor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
    transition: transform 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-10px) !important;
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
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.data-section:hover {
    transform: translateY(-5px);
    box-shadow: 0 25px 45px rgba(0,0,0,0.15);
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

.status-indicator.error {
    background: #f44336;
    animation: errorPulse 2s infinite;
}

.status-indicator.warning {
    background: #ff9800;
    animation: warningPulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(76, 175, 80, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }
}

@keyframes errorPulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(244, 67, 54, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(244, 67, 54, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(244, 67, 54, 0); }
}

@keyframes warningPulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 152, 0, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(255, 152, 0, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 152, 0, 0); }
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
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-weight: bold;
    animation: profitGlow 2s ease-in-out infinite alternate;
    font-size: 1.1rem;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
}

@keyframes profitGlow {
    from { box-shadow: 0 0 15px rgba(56, 239, 125, 0.5); }
    to { box-shadow: 0 0 25px rgba(17, 153, 142, 0.8); }
}

.info-message {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 1.5rem;
    border-radius: 15px;
    text-align: center;
    animation: infoFade 2s ease-in-out infinite alternate;
    font-size: 1.1rem;
}

.error-message {
    background: linear-gradient(135deg, #f44336, #d32f2f);
    color: white;
    padding: 1.5rem;
    border-radius: 15px;
    text-align: center;
    animation: errorFade 2s ease-in-out infinite alternate;
    font-size: 1.1rem;
}

.warning-message {
    background: linear-gradient(135deg, #ff9800, #f57c00);
    color: white;
    padding: 1.5rem;
    border-radius: 15px;
    text-align: center;
    animation: warningFade 2s ease-in-out infinite alternate;
    font-size: 1.1rem;
}

@keyframes infoFade {
    from { opacity: 0.8; }
    to { opacity: 1; }
}

@keyframes errorFade {
    from { opacity: 0.8; }
    to { opacity: 1; }
}

@keyframes warningFade {
    from { opacity: 0.8; }
    to { opacity: 1; }
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}

.stat-item {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    border: 1px solid rgba(102, 126, 234, 0.2);
    transition: transform 0.3s ease;
}

.stat-item:hover {
    transform: translateY(-3px);
}

.stat-number {
    font-size: 2rem;
    font-weight: bold;
    color: #667eea;
    font-family: 'Orbitron', monospace;
}

.stat-label {
    color: #666;
    font-size: 0.9rem;
    margin-top: 0.5rem;
}

/* Enhanced dataframe styling */
.stDataFrame {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    border: 1px solid rgba(102, 126, 234, 0.1);
}

.footer-stats {
    text-align: center;
    margin-top: 2rem;
    padding: 1.5rem;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
    border-radius: 15px;
    border: 1px solid rgba(102, 126, 234, 0.2);
}
</style>
""", unsafe_allow_html=True)

class RobustNSEPredictor:
    def __init__(self):
        self.data_queue = queue.Queue()
        self.error_queue = queue.Queue()
        self.last_fetch_time = None
        self.fetch_interval = 180  # 3 minutes instead of 10 seconds
        self.rate_limit_delay = 2  # 2 seconds between API calls
        self.max_retries = 3
        self.symbols_batch_size = 50  # Reduce batch size to avoid rate limiting
        
    def safe_fetch_data_to_csv(self):
        """Safely fetch data with rate limiting and error handling"""
        try:
            # Check if we should fetch data (rate limiting)
            current_time = datetime.now()
            if (self.last_fetch_time and 
                (current_time - self.last_fetch_time).total_seconds() < self.fetch_interval):
                return
            
            logger.info("Starting data fetch process...")
            symbols = fetch_all_nse_symbols()
            
            # Limit symbols and add random delay to avoid rate limiting
            limited_symbols = symbols[:self.symbols_batch_size]
            
            # Add jitter to avoid synchronized requests
            jitter = random.uniform(1, 5)
            time.sleep(jitter)
            
            # Fetch data with rate limiting
            fetch_nse_live_data(limited_symbols)
            
            self.last_fetch_time = current_time
            logger.info(f"Successfully fetched data for {len(limited_symbols)} symbols")
            
        except Exception as e:
            error_msg = f"Error fetching data: {str(e)}"
            logger.error(error_msg)
            self.error_queue.put(error_msg)
    
    def safe_predict_profit(self):
        """Safely predict profits with error handling"""
        try:
            if not os.path.exists("nse_live.csv"):
                return None
                
            df = pd.read_csv("nse_live.csv")
            if df.empty:
                return None
                
            df = df.dropna()
            
            if not os.path.exists("profit_prediction_model.pkl"):
                logger.error("Model file not found")
                return None
            
            model = pickle.load(open("profit_prediction_model.pkl", "rb"))
            
            required_columns = ['OPEN', 'HIGH', 'LOW', 'PREVCLOSE', 'LAST']
            if not all(col in df.columns for col in required_columns):
                logger.error(f"Missing required columns. Available: {df.columns.tolist()}")
                return None
            
            df['PREDICTED_PROFIT'] = model.predict(df[required_columns])
            df.to_csv("nse_live_with_profit.csv", index=False, mode='w')
            
            logger.info(f"Successfully predicted profits for {len(df)} stocks")
            return df
            
        except Exception as e:
            error_msg = f"Error in prediction: {str(e)}"
            logger.error(error_msg)
            self.error_queue.put(error_msg)
            return None
    
    def run_background_process_safe(self):
        """Run background process with proper error handling and rate limiting"""
        while True:
            try:
                # Fetch data
                self.safe_fetch_data_to_csv()
                
                # Wait a bit before prediction
                time.sleep(5)
                
                # Predict profits
                self.safe_predict_profit()
                
                # Wait for next cycle (3 minutes)
                time.sleep(self.fetch_interval)
                
            except Exception as e:
                error_msg = f"Background process error: {str(e)}"
                logger.error(error_msg)
                self.error_queue.put(error_msg)
                # Wait longer on error to avoid hammering
                time.sleep(300)  # 5 minutes

# Initialize the robust predictor
@st.cache_resource
def get_predictor():
    return RobustNSEPredictor()

predictor = get_predictor()

# Initialize session state
if 'background_started' not in st.session_state:
    st.session_state.background_started = True
    st.session_state.last_update = datetime.now()
    st.session_state.error_count = 0
    st.session_state.success_count = 0
    
    # Start background process with daemon thread
    background_thread = threading.Thread(
        target=predictor.run_background_process_safe, 
        daemon=True
    )
    background_thread.start()
    logger.info("Background process started")

# Beautiful Header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">⚡ NSE STOCK PREDICTOR ⚡</h1>
    <p class="subtitle">Real-time Market Analysis & AI-Powered Profit Predictions</p>
</div>
""", unsafe_allow_html=True)

# Check for errors and update status
error_status = "normal"
error_message = ""

try:
    while not predictor.error_queue.empty():
        error_message = predictor.error_queue.get_nowait()
        st.session_state.error_count += 1
        if "Rate limited" in error_message or "Too Many Requests" in error_message:
            error_status = "warning"
        else:
            error_status = "error"
except:
    pass

# Status indicators with dynamic status
col_status1, col_status2, col_status3 = st.columns(3)

with col_status1:
    status_class = "error" if error_status == "error" else ("warning" if error_status == "warning" else "")
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color: white; margin: 0;">🔄 Data Fetching</h3>
        <p style="color: rgba(255,255,255,0.8); margin: 0;">
            {"Rate Limited" if error_status == "warning" else ("Error" if error_status == "error" else "Live Updates")}
            <span class="status-indicator {status_class}"></span>
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_status2:
    model_exists = os.path.exists("profit_prediction_model.pkl")
    model_status = "" if model_exists else "error"
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color: white; margin: 0;">🤖 AI Engine</h3>
        <p style="color: rgba(255,255,255,0.8); margin: 0;">
            {"Predicting" if model_exists else "Model Missing"}
            <span class="status-indicator {model_status}"></span>
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_status3:
    data_exists = os.path.exists("nse_live.csv")
    data_status = "" if data_exists else "warning"
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color: white; margin: 0;">📊 Analysis</h3>
        <p style="color: rgba(255,255,255,0.8); margin: 0;">
            {"Real-time" if data_exists else "Loading"}
            <span class="status-indicator {data_status}"></span>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Show error message if exists
if error_message and error_status == "warning":
    st.markdown(f"""
    <div class="warning-message">
        ⚠️ Rate limiting detected. Slowing down requests to prevent API blocks.
    </div>
    """, unsafe_allow_html=True)
elif error_message and error_status == "error":
    st.markdown(f"""
    <div class="error-message">
        ❌ System Error: Please check logs for details.
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
            if not live_data.empty:
                # Add some statistics
                st.markdown(f"""
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-number">{len(live_data)}</div>
                        <div class="stat-label">Active Stocks</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{live_data['LAST'].mean():.1f}</div>
                        <div class="stat-label">Avg Price</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.dataframe(live_data, use_container_width=True, height=400)
                st.session_state.success_count += 1
            else:
                st.markdown('<div class="warning-message">📊 Data file exists but is empty. Fetching fresh data...</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-message">❌ Error loading data: {str(e)}</div>', unsafe_allow_html=True)
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
            if not profit_data.empty and 'PREDICTED_PROFIT' in profit_data.columns:
                top_3 = profit_data.nlargest(3, 'PREDICTED_PROFIT')
                
                # Add statistics
                st.markdown(f"""
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-number">{len(profit_data)}</div>
                        <div class="stat-label">Analyzed</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{profit_data['PREDICTED_PROFIT'].max():.2f}</div>
                        <div class="stat-label">Max Profit</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Style the profit column
                styled_df = top_3[['SYMBOL', 'LAST', 'PREDICTED_PROFIT']].copy()
                styled_df['PREDICTED_PROFIT'] = styled_df['PREDICTED_PROFIT'].round(2)
                styled_df['LAST'] = styled_df['LAST'].round(2)
                
                st.dataframe(styled_df, use_container_width=True, height=300)
                
                # Show top prediction as highlight
                if not top_3.empty:
                    top_stock = top_3.iloc[0]
                    st.markdown(f"""
                    <div style="text-align: center; margin-top: 1rem;">
                        <span class="profit-highlight">
                            🏆 Best Pick: {top_stock['SYMBOL']} - Predicted Profit: ₹{top_stock['PREDICTED_PROFIT']:.2f}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="warning-message">📊 Prediction data is incomplete. Recalculating...</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.markdown(f'<div class="error-message">❌ Error loading predictions: {str(e)}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-message"><span class="loading-spinner"></span> AI is calculating predictions...</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Enhanced footer with system statistics
current_time = datetime.now()
uptime = current_time - st.session_state.last_update if hasattr(st.session_state, 'last_update') else timedelta(0)

st.markdown(f"""
<div class="footer-stats">
    <div class="stats-grid">
        <div class="stat-item">
            <div class="stat-number">{int(uptime.total_seconds() // 60)}</div>
            <div class="stat-label">Minutes Running</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{st.session_state.success_count}</div>
            <div class="stat-label">Successful Updates</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{st.session_state.error_count}</div>
            <div class="stat-label">Rate Limit Hits</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">3</div>
            <div class="stat-label">Minute Intervals</div>
        </div>
    </div>
    <p style="color: #667eea; font-weight: 500; margin-top: 1rem;">
        🔄 Auto-refreshing every 3 minutes | 🤖 AI predictions with smart rate limiting | 
        ⏰ Last Update: {current_time.strftime("%H:%M:%S")}
    </p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh every 30 seconds instead of 5 to reduce load
time.sleep(30)
st.rerun()