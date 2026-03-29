import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def get_history(ticker: str, period: str, interval: str) -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)
    if data is None or data.empty:
        raise ValueError("No data found for the given parameters.")
    return data


def get_close_price(ticker: str) -> float:
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d")
    if hist is None or hist.empty or 'Close' not in hist.columns:
        raise ValueError("No close price available for the given ticker.")
    return float(hist['Close'].iloc[0])


def get_price_for_date(ticker: str, date: str) -> dict:
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD (e.g., '2018-03-11')")
    
    stock = yf.Ticker(ticker)
    start_date = date_obj.strftime('%Y-%m-%d')
    end_date = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')
    
    data = stock.history(start=start_date, end=end_date, interval='1d')
    
    if data is None or data.empty:
        raise ValueError(f"No data found for {ticker} on {date}. The market may have been closed on this date.")
    
    row = data.iloc[0]
    
    return {
        "date": date_obj.strftime('%Y-%m-%d'),
        "open": float(row['Open']),
        "high": float(row['High']),
        "low": float(row['Low']),
        "close": float(row['Close']),
        "volume": int(row['Volume']),
        "dividends": float(row.get('Dividends', 0.0)),
        "stock_splits": float(row.get('Stock Splits', 0.0))
    }
