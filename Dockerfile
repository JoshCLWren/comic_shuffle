FROM python:3.9.6 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app


RUN python -m venv .venv
COPY requirements.txt ./
RUN .venv/bin/pip install -r requirements.txt
FROM python:3.9.6-slim
RUN apt update && apt install -y ca-certificates
WORKDIR /app
COPY --from=builder /app/.venv .venv/
COPY . .
CMD ["/app/.venv/bin/streamlit", "run", "streamlit_app.py"]
