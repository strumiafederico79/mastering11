FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends     ffmpeg     curl     libsndfile1     ladspa-sdk     && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
COPY requirements-ai.txt /app/requirements-ai.txt
ARG ENABLE_AI_SEPARATION=0
RUN pip install --upgrade pip && pip install -r /app/requirements.txt
RUN if [ "$ENABLE_AI_SEPARATION" = "1" ]; then pip install -r /app/requirements-ai.txt; fi

COPY app /app/app
COPY frontend /app/frontend
COPY nginx /app/nginx

RUN mkdir -p /data/uploads /data/outputs /data/jobs /data/learning /app/references

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
