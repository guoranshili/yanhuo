# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0.0)
    down = -1*delta.clip(upper=0.0)
    ma_up = up.ewm(com=period-1, adjust=False).mean()
    ma_down = down.ewm(com=period-1, adjust=False).mean()
    rs = ma_up / (ma_down + 1e-9)
    return 100 - (100 / (1 + rs))

def macd(series: pd.Series, fast=12, slow=26, signal=9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def score_signals(close: pd.Series) -> dict:
    out = {"ma_trend":0,"rsi":0,"macd":0,"composite":0}
    if close is None or close.empty:
        return out
    ma20 = close.rolling(20).mean()
    ma60 = close.rolling(60).mean()
    trend = 1 if ma20.iloc[-1] > ma60.iloc[-1] else -1
    r = rsi(close).iloc[-1]
    r_score = 1 if 45 <= r <= 65 else (-1 if (r < 35 or r > 75) else 0)
    m_line, s_line, h = macd(close)
    m_score = 1 if m_line.iloc[-1] > s_line.iloc[-1] else -1
    comp = trend + r_score + m_score
    out.update({"ma_trend":trend,"rsi":r_score,"macd":m_score,"composite":comp})
    return out
