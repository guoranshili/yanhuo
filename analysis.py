# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

def _ensure_series(close):
    # 将 DataFrame/多层列/列表都规整为一维 Series
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, -1].squeeze()
    if not isinstance(close, pd.Series):
        close = pd.Series(close)
    close = pd.to_numeric(close, errors="coerce").dropna()
    return close

def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    if len(series) < period + 1:
        return pd.Series(index=series.index, dtype="float64")
    delta = series.diff()
    up = delta.clip(lower=0.0)
    down = -1 * delta.clip(upper=0.0)
    ma_up = up.ewm(com=period-1, adjust=False).mean()
    ma_down = down.ewm(com=period-1, adjust=False).mean()
    rs = ma_up / (ma_down.replace(0, np.nan))
    rsi_val = 100 - (100 / (1 + rs))
    return rsi_val

def macd(series: pd.Series, fast=12, slow=26, signal=9):
    if len(series) < slow + signal:
        idx = series.index
        nan = pd.Series([np.nan]*len(idx), index=idx)
        return nan, nan, nan
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def score_signals(close_input) -> dict:
    out = {"ma_trend": 0, "rsi": 0, "macd": 0, "composite": 0}
    close = _ensure_series(close_input)

    # 数据太短直接返回中性分
    if len(close) < 60:
        return out

    ma20 = close.rolling(20).mean()
    ma60 = close.rolling(60).mean()
    v20 = ma20.iloc[-1]
    v60 = ma60.iloc[-1]

    # 末值 NaN 则中性
    trend = 0 if (pd.isna(v20) or pd.isna(v60)) else (1 if float(v20) > float(v60) else -1)

    r_series = rsi(close)
    r = r_series.iloc[-1] if len(r_series) else np.nan
    if pd.isna(r):
        r_score = 0
    else:
        r_score = 1 if 45 <= r <= 65 else (-1 if (r < 35 or r > 75) else 0)

    m_line, s_line, _ = macd(close)
    if len(m_line.dropna()) == 0 or len(s_line.dropna()) == 0:
        m_score = 0
    else:
        m_score = 1 if float(m_line.iloc[-1]) > float(s_line.iloc[-1]) else -1

    comp = trend + r_score + m_score
    out.update({"ma_trend": trend, "rsi": r_score, "macd": m_score, "composite": comp})
    return out
