import yfinance as yf
import pandas as pd

def fetch_all_nse_symbols():
    df = pd.read_csv("symbols.csv")
    symbols = list(df['SYMBOL'])
    symbols = [f"{symbol}.NS" for symbol in symbols]
    return symbols


def fetch_nse_live_data(symbols):
    data = []  # Reset data list for each function call
    for sym in symbols:
        ticker = yf.Ticker(sym)
        try:
            info = ticker.info
            data.append({
                'SYMBOL': sym,
                'OPEN': info.get('open'),
                'HIGH': info.get('dayHigh'),
                'LOW': info.get('dayLow'),
                'PREVCLOSE': info.get('previousClose'),
                'LAST': info.get('currentPrice')
            })
        except Exception as e:
            print(f"⚠️ Could not fetch {sym}: {e}")

    df = pd.DataFrame(data)
    df.to_csv("nse_live.csv", index=False)
    print("✅ Saved to nse_live.csv")

if __name__ == '__main__':
    symbols = fetch_all_nse_symbols()
    fetch_nse_live_data(symbols[:4])