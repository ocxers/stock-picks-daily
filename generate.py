import yfinance as yf
import json
import random
from datetime import datetime, timedelta
import os

WATCHLIST = ['NVDA', 'TSLA', 'AMD', 'PLTR', 'S', 'AMBA', 'CRWD', 'SHOP', 'ABNB', 'COIN', 'MARA']
DATA_FILE = '/opt/data/stock-picks/data.json'
INITIAL_CAPITAL = 1000

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"current_picks": [], "history": []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_current_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if not hist.empty:
            return hist['Close'].iloc[-1]
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
    return None

def generate_picks():
    data = load_data()
    
    # 1. Update History with current prices for previous picks
    if data.get('current_picks'):
        today_str = datetime.now().strftime('%Y-%m-%d')
        yesterday_picks = []
        
        for pick in data['current_picks']:
            ticker = pick['ticker']
            entry_price = pick['entry_price']
            current_price = get_current_price(ticker)
            
            if current_price:
                pnl_pct = ((current_price - entry_price) / entry_price) * 100
                yesterday_picks.append({
                    "ticker": ticker,
                    "entry_price": entry_price,
                    "close_price": round(current_price, 2),
                    "pnl_pct": f"{pnl_pct:+.2f}%"
                })
        
        if yesterday_picks:
            data['history'].insert(0, {
                "date": datetime.now().strftime('%Y-%m-%d'), # Actually this is today's date for yesterday's picks review? No, let's keep it simple.
                "picks": yesterday_picks
            })
            # Keep only last 5 days of history
            data['history'] = data['history'][:5]

    # 2. Generate new picks for today
    selected = random.sample(WATCHLIST, min(2, len(WATCHLIST)))
    new_picks = []
    
    for ticker in selected:
        price = get_current_price(ticker)
        if price:
            new_picks.append({
                "ticker": ticker,
                "entry_price": round(price, 2),
                "date": datetime.now().strftime('%Y-%m-%d')
            })

    data['current_picks'] = new_picks
    save_data(data)
    
    print(f"Generated picks: {[p['ticker'] for p in new_picks]}")
    if data['history']:
        print(f"Updated history with {len(data['history'][0]['picks'])} previous picks.")

if __name__ == "__main__":
    generate_picks()
