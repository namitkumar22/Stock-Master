from nsepython import nse_quote
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Reduced thread count and batch size for cloud deployment
MAX_THREADS = 5  # Reduced from 30 to prevent rate limiting
RETRIES = 3      # Increased retries
BATCH_SIZE = 20  # Process fewer symbols at once
MIN_DELAY = 1    # Minimum delay between requests
MAX_DELAY = 3    # Maximum delay between requests

def fetch_all_nse_symbols():
    """Fetch and validate symbols list"""
    try:
        df = pd.read_csv("symbols.csv")
        symbols = list(df['SYMBOL'])
        logger.info(f"Loaded {len(symbols)} symbols from symbols.csv")
        return symbols
    except Exception as e:
        logger.error(f"Error loading symbols: {e}")
        return []

def fetch_symbol_data(sym):
    """Fetch data for a single symbol with enhanced error handling"""
    for attempt in range(RETRIES):
        try:
            # Add random delay between requests
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            
            quote = nse_quote(sym)
            if not quote:
                logger.warning(f"Empty response for {sym}")
                continue
                
            data = {
                'SYMBOL': sym,
                'OPEN': quote.get('priceInfo', {}).get('open'),
                'HIGH': quote.get('priceInfo', {}).get('intraDayHighLow', {}).get('max'),
                'LOW': quote.get('priceInfo', {}).get('intraDayHighLow', {}).get('min'),
                'PREVCLOSE': quote.get('priceInfo', {}).get('previousClose'),
                'LAST': quote.get('priceInfo', {}).get('lastPrice')
            }
            
            # Validate data
            if all(v is not None for v in data.values()):
                return data
            else:
                logger.warning(f"Incomplete data for {sym}")
                
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {sym}: {str(e)}")
            if attempt < RETRIES - 1:
                time.sleep(random.uniform(MIN_DELAY * 2, MAX_DELAY * 2))
    return None

def fetch_nse_live_data(symbols, max_threads=MAX_THREADS):
    """Fetch live data with batching and enhanced error handling"""
    try:
        all_data = []
        
        # Process symbols in smaller batches
        for i in range(0, len(symbols), BATCH_SIZE):
            batch = symbols[i:i + BATCH_SIZE]
            logger.info(f"Processing batch {i//BATCH_SIZE + 1} with {len(batch)} symbols")
            
            data = []
            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                futures = {executor.submit(fetch_symbol_data, sym): sym for sym in batch}
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        data.append(result)
            
            all_data.extend(data)
            
            # Add delay between batches
            if i + BATCH_SIZE < len(symbols):
                time.sleep(random.uniform(MIN_DELAY * 2, MAX_DELAY * 2))
        
        if not all_data:
            logger.error("No data fetched")
            return
            
        df = pd.DataFrame(all_data)
        
        # Validate dataframe
        if df.empty:
            logger.error("Empty dataframe created")
            return
            
        # Save data
        df.to_csv("nse_live.csv", index=False)
        logger.info(f"✅ Successfully fetched and saved data for {len(df)} stocks")
        
        return df
        
    except Exception as e:
        logger.error(f"Error in fetch_nse_live_data: {str(e)}")
        return None

if __name__ == '__main__':
    symbols = fetch_all_nse_symbols()
    if symbols:
        fetch_nse_live_data(symbols)