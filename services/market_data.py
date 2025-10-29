import yfinance as yf
import pandas as pd


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
