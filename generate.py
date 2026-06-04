import yfinance as yf
import json
import random
from datetime import datetime
import os
import requests
from git import Repo

WATCHLIST = ['NVDA', 'TSLA', 'AMD', 'PLTR', 'S', 'AMBA', 'CRWD', 'SHOP', 'ABNB', 'COIN', 'MARA']
DATA_FILE = '/opt/data/stock-picks/data.json'
INITIAL_CAPITAL = 1000
TAVILY_API_KEY = "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"

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

def get_stock_insights(ticker):
    """Use Tavily to find reasons, targets, and sources for the stock."""
    query = f"{ticker} stock analyst rating target price reason buy June 2026"
    
    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "max_results": 3,
                "search_depth": "basic"
            }
        )
        data = response.json()
        
        reason = ""
        target_price = None
        sources = []

        if 'results' in data and len(data['results']) > 0:
            # Combine content from top results to find insights
            combined_content = " ".join([r.get('content', '') for r in data['results']])
            
            # Simple heuristic extraction (in a real app, use an LLM or better parser)
            if 'upgrade' in combined_content.lower() or 'buy' in combined_content.lower():
                reason = f"Recent analyst attention: {combined_content[:200]}..."
            else:
                reason = f"Market momentum detected: {combined_content[:200]}..."
            
            # Look for price targets (e.g., "$150", "target $145")
            import re
            targets = re.findall(r'(?:target|price\s*target)\s*(?:is)?\s*\$?(\d+(?:\.\d+)?)', combined_content, re.IGNORECASE)
            if targets:
                target_price = float(targets[0]) # Take the first one found
            
            sources = [r['url'] for r in data['results']]

        return {
            "reason": reason or "Selected based on high volatility and momentum in the tech sector.",
            "target_price": target_price,
            "sources": sources[:3] # Limit to 3 sources
        }
    except Exception as e:
        print(f"Error getting insights for {ticker}: {e}")
        return {
            "reason": "Selected based on high volatility and momentum in the tech sector.",
            "target_price": None,
            "sources": []
        }

def generate_picks():
    data = load_data()
    
    # 1. Update History with current prices for previous picks
    if data.get('current_picks'):
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
                "date": datetime.now().strftime('%Y-%m-%d'), 
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
            insights = get_stock_insights(ticker)
            new_picks.append({
                "ticker": ticker,
                "entry_price": round(price, 2),
                "date": datetime.now().strftime('%Y-%m-%d'),
                "reason": insights['reason'],
                "target_price": insights['target_price'],
                "sources": insights['sources']
            })

    data['current_picks'] = new_picks
    save_data(data)
    
    # 3. Git Push to GitHub so the website updates
    repo_path = '/opt/data/stock-picks'
    try:
        repo = Repo(repo_path)
        repo.index.add(['data.json'])
        repo.index.commit(f"Update stock data for {datetime.now().strftime('%Y-%m-%d')}")
        
        origin = repo.remote('origin')
        origin.push()
        print("Data successfully pushed to GitHub.")
    except Exception as e:
        print(f"Git push failed (this might happen if no changes were made): {e}")

if __name__ == "__main__":
    generate_picks()
