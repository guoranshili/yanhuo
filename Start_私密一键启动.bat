@echo off
title 炎火智投（私密版）一键启动
setlocal ENABLEDELAYEDEXECUTION

if "%APP_PASSWORD%"=="" set APP_PASSWORD=guoran888

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [提示] 未检测到 Python。若未安装，請前往 https://www.python.org/downloads/ 安装 3.10+ 版本后重试。
    pause
    exit /b 1
)

if not exist venv (
  echo [1/3] 创建虚拟环境...
  python -m venv venv
)

call venv\Scripts\activate
echo [2/3] 安装依赖...
pip install --upgrade pip
pip install -r requirements.txt

echo [3/3] 启动服务（密码：%APP_PASSWORD%）...
start "" http://localhost:8501
streamlit run app_streamlit.py --server.address 0.0.0.0 --server.port 8501
