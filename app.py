from __future__ import annotations

from fastapi import FastAPI

from src.pipeline import run_pipeline


app = FastAPI(
    title="Document Intelligence MinIO Pipeline",
    description=(
        "Pipeline de document intelligence preparado para MinIO, com buckets raw, processed e curated "
        "e fallback local reproduzivel."
    ),
    version="1.0.0",
)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/run")
def run() -> dict[str, object]:
    return run_pipeline()
