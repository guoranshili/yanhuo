with tab1:
    t = st.text_input("单标代码", value="600519.SS")
    if st.button("获取单标数据", type="primary"):
        df = get_history(t, period=period, interval=interval, prefer=prefer)
        if df is None or df.empty or "Close" not in df.columns:
            st.error("未获取到数据，请检查代码或数据源。")
        else:
            close = df["Close"]
            # 关键：如果 Close 还是 DataFrame 或多层列，压成一维
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, -1].squeeze()
            close = pd.to_numeric(close, errors="coerce")

            st.line_chart(close.dropna())
            sig = score_signals(close)
            st.write("**信号打分**：", sig)
            if close.dropna().empty:
                st.warning("末端价格为空，无法显示最新价。")
            else:
                last = float(close.dropna().iloc[-1])
                st.metric("最新价", f"{last:.3f}")
