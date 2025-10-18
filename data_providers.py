# -*- coding: utf-8 -*-
from __future__ import annotations
import datetime as dt
from typing import Optional
import pandas as pd

try:
    import yfinance as yf
except Exception:
    yf = None

try:
    import akshare as ak
except Exception:
    ak = None

def normalize_cn_ticker(ticker: str) -> str:
    t = ticker.strip().upper()
    if t.endswith(".SS") or t.endswith(".SZ"):
        return t
    if len(t) == 6 and t.isdigit():
        if t.startswith(("600","601","603","605")):
            return t + ".SS"
        elif t.startswith(("000","001","002","003")):
            return t + ".SZ"
    return t

def yf_history(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    if yf is None:
        return pd.DataFrame()
    t = normalize_cn_ticker(ticker)
    df = yf.download(t, period=period, interval=interval, auto_adjust=True, progress=False)
    if isinstance(df, pd.DataFrame) and not df.empty:
        df = df.rename(columns=str.capitalize)
    return df

def ak_history(ticker: str, period_days: int = 365) -> pd.DataFrame:
    if ak is None:
        return pd.DataFrame()
    try:
        df = ak.stock_zh_a_hist(symbol=ticker, period="daily",
                                start_date=(dt.date.today()-dt.timedelta(days=period_days)).strftime("%Y%m%d"),
                                end_date=None, adjust="qfq")
        df = df.rename(columns={"日期":"Date","开盘":"Open","收盘":"Close","最高":"High","最低":"Low","成交量":"Volume"})
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date").sort_index()
        return df[["Open","High","Low","Close","Volume"]]
    except Exception:
        return pd.DataFrame()

def get_history(ticker: str, period: str = "1y", interval: str = "1d", prefer: str = "auto") -> pd.DataFrame:
    if prefer == "ak":
        df = ak_history(ticker)
        if not df.empty:
            return df
        return yf_history(ticker, period=period, interval=interval)
    else:
        df = yf_history(ticker, period=period, interval=interval)
        if not df.empty:
            return df
        return ak_history(ticker)

def latest_price(ticker: str) -> Optional[float]:
    df = yf_history(ticker, period="5d", interval="1m")
    if df is None or df.empty:
        return None
    try:
        return float(df["Close"].dropna().iloc[-1])
    except Exception:
        return None
