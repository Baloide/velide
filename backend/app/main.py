from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.schemas.ingest import FileFormat, IngestResponse
from app.schemas.redact import RedactRequest, RedactResponse
from app.services.languages import SAMPLES
from app.services.redaction_engine import RedactionEngine
from app.services.text_ingestion import MAX_FILE_BYTES, IngestionError, extract_text

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Local clinical text de-identification with review.",
    docs_url=None,
    redoc_url=None,
)
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "[::1]", "testserver"]
)
engine = RedactionEngine()
STATIC_DIR = Path(__file__).parent / "static"
DOWNLOAD_DIR = Path(__file__).resolve().parents[2] / "dist"
WINDOWS_PACKAGE = "Velide-Windows.zip"


@app.middleware("http")
async def privacy_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    )
    return response


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME, "version": settings.VERSION}


@app.get("/api/sample")
def sample(language: Literal["it", "en", "es", "de", "fr", "pt", "nl", "pl", "tr", "ru"] = "en"):
    return {"sample": SAMPLES[language]}


@app.post("/api/redact/text", response_model=RedactResponse)
def redact_text(req: RedactRequest):
    return engine.redact(req.text, req.options)


@app.post("/api/ingest/file", response_model=IngestResponse)
async def ingest_file(request: Request, format: FileFormat):
    # Raw upload avoids multipart spooling to disk, including for large documents.
    data = bytearray()
    async for chunk in request.stream():
        if len(data) + len(chunk) > MAX_FILE_BYTES:
            raise HTTPException(413, detail={"code": "fileTooLarge"})
        data.extend(chunk)
    try:
        return await run_in_threadpool(extract_text, bytes(data), format)
    except IngestionError as error:
        raise HTTPException(error.status, detail={"code": error.code}) from None


@app.get("/api/downloads")
def downloads():
    return {"windows": "/download/windows" if (DOWNLOAD_DIR / WINDOWS_PACKAGE).is_file() else None}


@app.get("/download/windows")
def download_windows():
    package = DOWNLOAD_DIR / WINDOWS_PACKAGE
    if not package.is_file():
        raise HTTPException(404, "Windows package has not been built on this host.")
    return FileResponse(package, filename=WINDOWS_PACKAGE, media_type="application/zip")


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")
