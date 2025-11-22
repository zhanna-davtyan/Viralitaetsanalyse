from fastapi import FastAPI, UploadFile, File, HTTPException
from contextlib import asynccontextmanager
import logging
from pathlib import Path

try:
    # import database helper from the backend package
    import backend.database as database
except Exception:
    # best-effort import; database module is expected to live in backend/database.py
    database = None

logger = logging.getLogger("viralytics.backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler replacing deprecated on_event startup/shutdown.

    Initializes the database at application startup when available.
    """
    if database is not None:
        try:
            database.init_db()
            logger.info("Database initialized on startup")
        except Exception as e:
            logger.warning(f"Database init failed on startup: {e}")
    yield
    # place for shutdown cleanup in future


app = FastAPI(title="Viralytics Backend", lifespan=lifespan)


@app.get("/health")
async def health():
    """Simple health endpoint."""
    return {"status": "ok"}


# Placeholder for future endpoints
@app.get("/")
async def root():
    return {"message": "Viralytics backend - FastAPI running"}


# Upload directory (project-root / uploads)
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Receive a video upload and store it in the uploads directory.

    This endpoint currently only saves the uploaded file and returns
    a confirmation JSON. No feature extraction or model inference is invoked.
    """
    # sanitize filename
    filename = Path(file.filename).name
    dest = UPLOAD_DIR / filename

    try:
        contents = await file.read()
        with open(dest, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {e}")
    finally:
        await file.close()

    return {"status": "received", "filename": str(dest.name)}


if __name__ == "__main__":
    # Optional development server start (uvicorn may or may not be installed)
    try:
        import uvicorn

        uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
    except Exception:
        print("uvicorn not available - run the app with an ASGI server of your choice")
