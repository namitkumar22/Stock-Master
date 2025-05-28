from nsepython import nse_quote
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

MAX_THREADS = 30  # Adjust between 20-50 based on your testing
RETRIES = 2       # Retry failed requests this many times

def fetch_all_nse_symbols():
    df = pd.read_csv("symbols.csv")
    return list(df['SYMBOL'])

def fetch_symbol_data(sym):
    for attempt in range(RETRIES):
        try:
            quote = nse_quote(sym)
            return {
                'SYMBOL': sym,
                'OPEN': quote.get('priceInfo', {}).get('open'),
                'HIGH': quote.get('priceInfo', {}).get('intraDayHighLow', {}).get('max'),
                'LOW': quote.get('priceInfo', {}).get('intraDayHighLow', {}).get('min'),
                'PREVCLOSE': quote.get('priceInfo', {}).get('previousClose'),
                'LAST': quote.get('priceInfo', {}).get('lastPrice')
            }
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed for {sym}: {e}")
            time.sleep(0.2)  # Small delay before retry
    return None

def fetch_nse_live_data(symbols, max_threads=MAX_THREADS):
    data = []
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(fetch_symbol_data, sym): sym for sym in symbols}
        for future in as_completed(futures):
            result = future.result()
            if result:
                data.append(result)

    df = pd.DataFrame(data)
    df.to_csv("nse_live.csv", index=False)
    print(f"✅ Fetched and saved live data for {len(data)} stocks to nse_live.csv")

if __name__ == '__main__':
    symbols = fetch_all_nse_symbols()
    fetch_nse_live_data(symbols)  # Fetch 50 at once (increase as per stability)
