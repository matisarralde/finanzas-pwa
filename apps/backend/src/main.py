# apps/backend/src/main.py
from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="Finanzas PWA - Backend (bootstrap)")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
