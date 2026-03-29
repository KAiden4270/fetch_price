import pandas as pd
import pandas_ta as ta


def compute_rsi(close_series: pd.Series, length: int) -> pd.Series:
    return ta.rsi(close_series, length=length)


def compute_macd(close_series: pd.Series, fast: int, slow: int, signal: int) -> pd.DataFrame:
    return ta.macd(close_series, fast=fast, slow=slow, signal=signal)


def compute_moving_averages(close_series: pd.Series, sma_periods: list[int], ema_periods: list[int]) -> dict:
    result: dict[str, pd.Series] = {}
    for p in sma_periods:
        result[f'SMA_{p}'] = ta.sma(close_series, length=p)
    for p in ema_periods:
        result[f'EMA_{p}'] = ta.ema(close_series, length=p)
    return result
