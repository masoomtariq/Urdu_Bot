FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=7860 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    ffmpeg \
    tar \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./

RUN mkdir -p /app/piper \
    && curl -L "https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz" -o /tmp/piper_linux_x86_64.tar.gz \
    && tar -xzf /tmp/piper_linux_x86_64.tar.gz -C /app/piper --strip-components=1 \
    && chmod +x /app/piper/piper \
    && rm -f /tmp/piper_linux_x86_64.tar.gz \
    && curl -L "https://huggingface.co/IhorShevchuk/piper-voice-ur-fasih/resolve/main/ur_PK-fasih-medium-model.onnx" -o /app/ur_PK-fasih-medium-model.onnx \
    && curl -L "https://huggingface.co/IhorShevchuk/piper-voice-ur-fasih/resolve/main/ur_PK-fasih-medium-model.onnx.json" -o /app/ur_PK-fasih-medium-model.onnx.json

EXPOSE 7860

CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0", "--server.port=7860"]