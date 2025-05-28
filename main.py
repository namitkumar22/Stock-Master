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
from typing import Optional, Dict, Any
import json

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

# Configure page
st.set_page_config(
    page_title="✨ NSE Stock Predictor Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "### NSE Stock Predictor Pro\nPowered by Advanced AI and Real-time Market Analytics",
        'Get Help': 'https://github.com/your-repo/nse-predictor',
        'Report a bug': 'https://github.com/your-repo/nse-predictor/issues'
    }
)

# Enhanced CSS with better animations and responsiveness
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto:wght@300;400;500&display=swap');

/* Base Styles */
body {
    font-family: 'Roboto', sans-serif;
    background-color: #f4f7fa;
    margin: 0;
    padding: 0;
}

h1, h2, h3 {
    font-family: 'Orbitron', monospace;
    color: #333;
    margin: 0;
    padding: 0;
}

/* Header Styles */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #6B8DD6 100%);
    background-size: 200% 200%;
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
}

.subtitle {
    font-family: 'Roboto', sans-serif;
    color: rgba(255,255,255,0.9);
    font-size: 1.2rem;
    margin-top: 0.5rem;
}

/* Card and Section Styles */
.metric-card {
    background: linear-gradient(145deg, #1e3c72, #2a5298);
    padding: 1.5rem;
    border-radius: 15px;
    margin: 0.5rem;
    height: 100%;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    border: 1px solid rgba(255,255,255,0.1);
    transition: transform 0.3s ease;
    animation: floatUp 0.8s ease-out;
}

.metric-card:hover {
    transform: translateY(-5px);
}

.data-section {
    background: linear-gradient(145deg, #f6f9fc, #ffffff);
    padding: 2rem;
    border-radius: 20px;
    max-width: 100%;
    margin: 1rem auto;
    box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    border: 1px solid rgba(102, 126, 234, 0.1);
    transition: transform 0.3s ease;
    animation: floatUp 0.8s ease-out;
}

.data-section:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}

.section-title {
    font-family: 'Orbitron', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
    text-align: center;
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
}

.status-indicator.warning {
    background: #ff9800;
}

@keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(76, 175, 80, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }
}

.profit-highlight {
    background: linear-gradient(-45deg, #11998e, #38ef7d, #11998e);
    background-size: 200% 200%;
    animation: gradientFlow 5s ease infinite;
    color: white;
    padding: 1rem 2rem;
    border-radius: 25px;
    font-weight: bold;
    font-size: 1.1rem;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    display: inline-block;
    margin: 1rem auto;
    width: fit-content;
}

.alert-message {
    padding: 1.2rem;
    border-radius: 12px;
    margin: 1rem 0;
    font-weight: 500;
    text-align: center;
}

.alert-info {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
}

.alert-warning {
    background: linear-gradient(135deg, #ff9800, #f57c00);
    color: white;
}

.alert-error {
    background: linear-gradient(135deg, #f44336, #d32f2f);
    color: white;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    align-items: stretch;
    justify-content: center;
    margin: 1.5rem 0;
}

.stat-item {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 1.5rem;
    animation: floatUp 0.8s ease-out;
}

.stat-number {
    font-size: 1.8rem;
    font-weight: bold;
    color: #667eea;
    font-family: 'Orbitron', monospace;
}

.stat-label {
    color: #666;
    font-size: 0.9rem;
    margin-top: 0.5rem;
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

/* Enhanced Animations */
@keyframes floatUp {
    0% { transform: translateY(20px); opacity: 0; }
    100% { transform: translateY(0); opacity: 1; }
}

@keyframes gradientFlow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Updated Component Styles */
.main-header {
    animation: floatUp 0.8s ease-out, gradientFlow 15s ease infinite;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #6B8DD6 100%);
    background-size: 200% 200%;
    margin: 0 auto 2rem auto;
    max-width: 1200px;
}

.data-section {
    animation: floatUp 0.8s ease-out;
    max-width: 100%;
    margin: 1rem auto;
}

.metric-card {
    animation: floatUp 0.8s ease-out;
    margin: 0.5rem;
    height: 100%;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    align-items: stretch;
    justify-content: center;
    margin: 1.5rem 0;
}

.stat-item {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 1.5rem;
    animation: floatUp 0.8s ease-out;
}

.profit-highlight {
    background: linear-gradient(-45deg, #11998e, #38ef7d, #11998e);
    background-size: 200% 200%;
    animation: gradientFlow 5s ease infinite;
    width: fit-content;
    margin: 1rem auto;
    padding: 1rem 2rem;
}

/* Ensure consistent spacing */
.section-title {
    text-align: center;
    margin-bottom: 2rem;
}

[data-testid="stDataFrame"] {
    width: 100% !important;
    margin: 1rem 0;
}

</style>
""", unsafe_allow_html=True)

class RobustNSEPredictor:
    def __init__(self):
        self.data_queue = queue.Queue()
        self.error_queue = queue.Queue()
        self.status_queue = queue.Queue()
        self.last_fetch_time = None
        self.fetch_interval = 0  # 5 minutes for better stability
        self.rate_limit_delay = 0  # 3 seconds between API calls
        self.max_retries = 3
        self.symbols_batch_size = 100  # Smaller batch for reliability
        self.is_fetching = False
        self.last_successful_fetch = None
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            'data_file_exists': os.path.exists("nse_live.csv"),
            'model_file_exists': os.path.exists("profit_prediction_model.pkl"),
            'prediction_file_exists': os.path.exists("nse_live_with_profit.csv"),
            'is_fetching': self.is_fetching,
            'last_fetch': self.last_fetch_time,
            'last_successful_fetch': self.last_successful_fetch,
            'data_freshness': self.get_data_freshness(),
            'error_count': 0
        }
        return status
    
    def get_data_freshness(self) -> str:
        """Check how fresh the data is"""
        if not os.path.exists("nse_live.csv"):
            return "No data"
        
        try:
            file_time = datetime.fromtimestamp(os.path.getmtime("nse_live.csv"))
            age = datetime.now() - file_time
            if age.total_seconds() < 300:  # 5 minutes
                return "Fresh"
            elif age.total_seconds() < 900:  # 15 minutes
                return "Recent"
            else:
                return "Stale"
        except:
            return "Unknown"
    
    def safe_fetch_data(self) -> bool:
        """Safely fetch data with comprehensive error handling"""
        if self.is_fetching:
            return False
            
        try:
            self.is_fetching = True
            current_time = datetime.now()
            
            # Rate limiting check
            if (self.last_fetch_time and 
                (current_time - self.last_fetch_time).total_seconds() < self.fetch_interval):
                return False
            
            logger.info("Starting safe data fetch...")
            
            # Fetch symbols with retry logic
            for attempt in range(self.max_retries):
                try:
                    symbols = fetch_all_nse_symbols()
                    if symbols:
                        break
                    time.sleep(self.rate_limit_delay * (attempt + 1))
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == self.max_retries - 1:
                        raise e
                    time.sleep(self.rate_limit_delay * (attempt + 1))
            
            # Randomly sample 200 symbols
            if len(symbols) > self.symbols_batch_size:
                limited_symbols = random.sample(symbols, self.symbols_batch_size)
            else:
                limited_symbols = symbols
                
            jitter = random.uniform(2, 5)
            time.sleep(jitter)
            
            # Fetch live data with retry logic
            for attempt in range(self.max_retries):
                try:
                    fetch_nse_live_data(limited_symbols)
                    break
                except Exception as e:
                    logger.warning(f"Data fetch attempt {attempt + 1} failed: {str(e)}")
                    if attempt == self.max_retries - 1:
                        raise e
                    time.sleep(self.rate_limit_delay * (attempt + 1))
            
            self.last_fetch_time = current_time
            self.last_successful_fetch = current_time
            logger.info(f"Successfully fetched data for {len(limited_symbols)} symbols")
            return True
            
        except Exception as e:
            error_msg = f"Data fetch error: {str(e)}"
            logger.error(error_msg)
            self.error_queue.put(error_msg)
            return False
        finally:
            self.is_fetching = False
    
    def safe_predict_profit(self) -> Optional[pd.DataFrame]:
        """Safely predict profits with validation"""
        try:
            # Validate data file
            if not os.path.exists("nse_live.csv"):
                logger.warning("No live data file found")
                return None
            
            df = pd.read_csv("nse_live.csv")
            if df.empty:
                logger.warning("Live data file is empty")
                return None
            
            # Clean data
            df = df.dropna()
            if df.empty:
                logger.warning("No valid data after cleaning")
                return None
            
            # Validate model
            if not os.path.exists("profit_prediction_model.pkl"):
                logger.error("Prediction model not found")
                return None
            
            with open("profit_prediction_model.pkl", "rb") as f:
                model = pickle.load(f)
            
            # Validate required columns
            required_columns = ['OPEN', 'HIGH', 'LOW', 'PREVCLOSE', 'LAST']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Missing required columns: {missing_columns}")
                return None
            
            # Make predictions
            features = df[required_columns].fillna(df[required_columns].mean())
            df['PREDICTED_PROFIT'] = model.predict(features)
            
            # Save predictions
            df.to_csv("nse_live_with_profit.csv", index=False)
            logger.info(f"Successfully predicted profits for {len(df)} stocks")
            return df
            
        except Exception as e:
            error_msg = f"Prediction error: {str(e)}"
            logger.error(error_msg)
            self.error_queue.put(error_msg)
            return None
    
    def background_worker(self):
        """Main background worker with enhanced error handling"""
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while True:
            try:
                # Fetch data
                if self.safe_fetch_data():
                    consecutive_errors = 0
                    time.sleep(10)  # Wait before prediction
                    
                    # Predict profits
                    result = self.safe_predict_profit()
                    if result is not None:
                        self.status_queue.put("success")
                    else:
                        consecutive_errors += 1
                else:
                    consecutive_errors += 1
                
                # Adaptive sleep based on errors
                if consecutive_errors > 0:
                    sleep_time = min(self.fetch_interval * (1 + consecutive_errors), 1800)  # Max 30 min
                    logger.warning(f"Sleeping for {sleep_time}s due to {consecutive_errors} consecutive errors")
                    time.sleep(sleep_time)
                else:
                    time.sleep(self.fetch_interval)
                
                # Emergency stop if too many consecutive errors
                if consecutive_errors >= max_consecutive_errors:
                    logger.critical("Too many consecutive errors, stopping background worker")
                    self.error_queue.put("Background worker stopped due to repeated failures")
                    break
                    
            except Exception as e:
                consecutive_errors += 1
                error_msg = f"Background worker critical error: {str(e)}"
                logger.critical(error_msg)
                self.error_queue.put(error_msg)
                time.sleep(600)  # 10 minutes on critical error

# Initialize predictor
@st.cache_resource
def get_predictor():
    return RobustNSEPredictor()

predictor = get_predictor()

# Initialize session state
if 'background_started' not in st.session_state:
    st.session_state.background_started = True
    st.session_state.start_time = datetime.now()
    st.session_state.error_count = 0
    st.session_state.success_count = 0
    st.session_state.last_status_check = datetime.now()
    
    # Start background worker
    background_thread = threading.Thread(target=predictor.background_worker, daemon=True)
    background_thread.start()
    logger.info("Robust background worker started")

# Header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">⚡ NSE STOCK PREDICTOR ⚡</h1>
    <p class="subtitle">Enterprise-Grade Market Analysis & AI-Powered Predictions</p>
</div>
""", unsafe_allow_html=True)

# System status monitoring
system_status = predictor.get_system_status()

# Process status updates
try:
    while not predictor.error_queue.empty():
        error = predictor.error_queue.get_nowait()
        st.session_state.error_count += 1
        logger.error(f"UI Error: {error}")
        
    while not predictor.status_queue.empty():
        status = predictor.status_queue.get_nowait()
        if status == "success":
            st.session_state.success_count += 1
except:
    pass

# Status cards
col1, col2, col3 = st.columns(3)

with col1:
    fetch_status = "error" if not system_status['data_file_exists'] else ("warning" if system_status['data_freshness'] == "Stale" else "")
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color: white; margin: 0;">🔄 Data Pipeline</h3>
        <p style="color: rgba(255,255,255,0.8); margin: 0;">
            {system_status['data_freshness']} Data
            <span class="status-indicator {fetch_status}"></span>
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    model_status = "error" if not system_status['model_file_exists'] else ""
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color: white; margin: 0;">🤖 AI Engine</h3>
        <p style="color: rgba(255,255,255,0.8); margin: 0;">
            {"Model Ready" if system_status['model_file_exists'] else "Model Missing"}
            <span class="status-indicator {model_status}"></span>
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    prediction_status = "error" if not system_status['prediction_file_exists'] else ""
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color: white; margin: 0;">📊 Predictions</h3>
        <p style="color: rgba(255,255,255,0.8); margin: 0;">
            {"Analysis Ready" if system_status['prediction_file_exists'] else "Processing"}
            <span class="status-indicator {prediction_status}"></span>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Main content
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("""
    <div class="data-section">
        <h2 class="section-title">📈 Live Market Data</h2>
    """, unsafe_allow_html=True)
    
    if system_status['data_file_exists']:
        try:
            live_data = pd.read_csv("nse_live.csv")
            if not live_data.empty:
                # Market statistics with error handling
                try:
                    avg_price = live_data['LAST'].mean() if 'LAST' in live_data.columns else 0
                except Exception:
                    avg_price = 0
                    logger.warning("Failed to calculate average price")

                st.markdown(f"""
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-number">2034</div>
                        <div class="stat-label">Active Stocks</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">₹{avg_price:.0f}</div>
                        <div class="stat-label">Avg Price</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display data with validation
                display_columns = ['SYMBOL', 'LAST', 'OPEN', 'HIGH', 'LOW', 'CHANGE', 'PCHANGE']
                available_columns = [col for col in display_columns if col in live_data.columns]
                if available_columns:
                    display_data = live_data[available_columns].copy()
                    # Clean data by removing invalid entries
                    display_data = display_data.dropna(subset=['SYMBOL', 'LAST'])
                    display_data = display_data[display_data['LAST'] > 0]
                    st.dataframe(display_data, use_container_width=True, height=350)
                else:
                    st.markdown('<div class="alert-message alert-warning">⚠️ Required columns not found in data</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-message alert-warning">📊 Data file is empty. Refreshing...</div>', unsafe_allow_html=True)
        except pd.errors.EmptyDataError:
            st.markdown('<div class="alert-message alert-error">❌ Empty data file detected</div>', unsafe_allow_html=True)
            logger.error("Empty data file detected")
        except Exception as e:
            st.markdown(f'<div class="alert-message alert-error">❌ Error loading data: {str(e)}</div>', unsafe_allow_html=True)
            logger.error(f"Error loading market data: {str(e)}")
    else:
        st.markdown('<div class="alert-message alert-info"><span class="loading-spinner"></span> Initializing market data feed...</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div class="data-section">
        <h2 class="section-title">🎯 AI Profit Predictions</h2>
    """, unsafe_allow_html=True)
    
    if system_status['prediction_file_exists']:
        try:
            profit_data = pd.read_csv("nse_live_with_profit.csv")
            if not profit_data.empty and 'PREDICTED_PROFIT' in profit_data.columns:
                # Get top predictions
                top_predictions = profit_data.nlargest(5, 'PREDICTED_PROFIT')
                
                # Prediction statistics (removed avg_profit)
                max_profit = profit_data['PREDICTED_PROFIT'].max()
                
                st.markdown(f"""
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-number">{len(profit_data)}</div>
                        <div class="stat-label">Stocks Analyzed</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">₹{max_profit:.2f}</div>
                        <div class="stat-label">Maximum Potential</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display top predictions
                display_df = top_predictions[['SYMBOL', 'LAST', 'PREDICTED_PROFIT']].copy()
                display_df['LAST'] = display_df['LAST'].round(2)
                display_df['PREDICTED_PROFIT'] = display_df['PREDICTED_PROFIT'].round(2)
                st.dataframe(display_df, use_container_width=True, height=250)
                
                # Highlight best prediction
                if not top_predictions.empty:
                    best = top_predictions.iloc[0]
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div class="profit-highlight">
                            🏆 Top Pick: {best['SYMBOL']} - Predicted: ₹{best['PREDICTED_PROFIT']:.2f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-message alert-warning">🤖 Predictions are being calculated...</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="alert-message alert-error">❌ Prediction error: {str(e)}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-message alert-info"><span class="loading-spinner"></span> AI is analyzing market data...</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# System statistics footer
if 'refresh_counter' not in st.session_state:
    st.session_state.refresh_counter = 0

# Clear previous elements on refresh
if st.session_state.refresh_counter > 0:
    st.empty()

uptime = datetime.now() - st.session_state.start_time
st.markdown(f"""
<div class="data-section" style="margin-top: 2rem;">
    <h3 style="text-align: center; color: #667eea; margin-bottom: 1rem;">📊 System Performance</h3>
    <div class="stats-grid">
        <div class="stat-item">
            <div class="stat-number">{int(uptime.total_seconds() // 60)}</div>
            <div class="stat-label">Minutes Online</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{st.session_state.success_count}</div>
            <div class="stat-label">Successful Updates</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{st.session_state.error_count}</div>
            <div class="stat-label">Errors Handled</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">5</div>
            <div class="stat-label">Sec Refresh</div>
        </div>
    </div>
    <p style="text-align: center; color: #667eea; margin-top: 1rem;">
        🔄 Auto-updating every 5 minutes | 🛡️ Enterprise-grade reliability | ⏰ {datetime.now().strftime("%H:%M:%S")}
    </p>
</div>
""", unsafe_allow_html=True)

# Update refresh counter and handle auto-refresh
st.session_state.refresh_counter += 1
time.sleep(5)

# Use a container to prevent duplicates
with st.empty():
    st.rerun()