# -*- coding: utf-8 -*-
import os
import streamlit as st
import pandas as pd
from data_providers import get_history, latest_price, normalize_cn_ticker
from analysis import score_signals

APP_TITLE = "🔥 炎火智投 - 郭先生版（私密）"
PASSWORD = os.environ.get("APP_PASSWORD", "guoran888")

st.set_page_config(page_title=APP_TITLE, layout="wide")

# --- Simple Password Gate ---
if "authed" not in st.session_state:
    st.session_state.authed = False

if not st.session_state.authed:
    st.title(APP_TITLE)
    st.info("本页面受密码保护。请输入访问密码。")
    pwd = st.text_input("访问密码", type="password")
    if st.button("进入"):
        if pwd == PASSWORD:
            st.session_state.authed = True
            st.experimental_rerun()
        else:
            st.error("密码错误。")
    st.stop()

# --- Main App ---
st.title(APP_TITLE)
st.caption("联网行情与信号面板（yfinance + 可选 akshare）。仅供学习研究，不构成投资建议。")

with st.sidebar:
    st.header("设置")
    default_tickers = "600519.SS, 601318.SS, 000001.SZ, 0700.HK, AAPL, NVDA, ^GSPC"
    tickers = st.text_input("观察标的（逗号分隔）", value=default_tickers)
    period = st.selectbox("周期", ["1mo","3mo","6mo","1y","2y","5y"], index=2)
    interval = st.selectbox("间隔", ["1d","1h","30m","15m"], index=0)
    prefer = st.selectbox("数据源优先", ["auto","ak"], index=0)

tab1, tab2 = st.tabs(["📊 单标分析", "🧺 批量打分"])

with tab1:
    t = st.text_input("单标代码", value="600519.SS")
    if st.button("获取单标数据", type="primary"):
        df = get_history(t, period=period, interval=interval, prefer=prefer)
        if df is None or df.empty:
            st.error("未获取到数据，请检查代码或数据源。")
        else:
            st.line_chart(df["Close"])
            sig = score_signals(df["Close"])
            st.write("**信号打分**：", sig)
            last = float(df["Close"].dropna().iloc[-1])
            st.metric("最新价", f"{last:.3f}")

with tab2:
    codes = [normalize_cn_ticker(x.strip()) for x in tickers.split(",") if x.strip()]
    rows = []
    for code in codes:
        df = get_history(code, period=period, interval=interval, prefer=prefer)
        if df is None or df.empty:
            rows.append({"代码":code,"最新价":"-","MA趋势":0,"RSI":0,"MACD":0,"合成分":0})
        else:
            sig = score_signals(df["Close"])
            last = float(df["Close"].dropna().iloc[-1])
            rows.append({"代码":code,"最新价":round(last,3),"MA趋势":sig["ma_trend"],"RSI":sig["rsi"],"MACD":sig["macd"],"合成分":sig["composite"]})
    st.dataframe(pd.DataFrame(rows))

st.info("A股：上交所 .SS（600519.SS），深交所 .SZ（000001.SZ）；港股 .HK；美股直接代码；指数如 ^GSPC。")
