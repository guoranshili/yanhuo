FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    APP_PASSWORD=changeme
EXPOSE 8501
CMD ["streamlit","run","app_streamlit.py","--server.port=8501","--server.address=0.0.0.0"]
