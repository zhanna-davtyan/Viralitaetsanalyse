from fastapi import FastAPI, UploadFile, File, HTTPException
from contextlib import asynccontextmanager
import logging
from pathlib import Path
from typing import Optional
import joblib
import pandas as pd
import json
import numpy as np

try:
    # import database helper from the backend package
    import backend.database as database
except Exception:
    # best-effort import; database module is expected to live in backend/database.py
    database = None

try:
    import feature_extractor
except Exception:
    feature_extractor = None

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
    # Load trained model once at startup
    model_path = Path(__file__).resolve().parent.parent / "results" / "best_model_XGBoost.pkl"
    app.state.model = None
    if model_path.exists():
        try:
            app.state.model = joblib.load(str(model_path))
            logger.info(f"Loaded model from {model_path}")
        except Exception as e:
            logger.warning(f"Failed to load model {model_path}: {e}")
    else:
        logger.warning(f"Model file not found at {model_path}; prediction endpoint will be unavailable")

    # Ensure feature_extractor is available
    if feature_extractor is None:
        try:
            import feature_extractor as feat
            app.state.feature_extractor = feat
        except Exception:
            app.state.feature_extractor = None
    else:
        app.state.feature_extractor = feature_extractor
    # Load feature names used during training (if available)
    feature_names_path = Path(__file__).resolve().parent.parent / "results" / "feature_names.json"
    if feature_names_path.exists():
        try:
            with open(feature_names_path, "r", encoding="utf-8") as fh:
                app.state.feature_names = json.load(fh)
                logger.info(f"Loaded feature names ({len(app.state.feature_names)}) from {feature_names_path}")
        except Exception as e:
            app.state.feature_names = None
            logger.warning(f"Failed to load feature names: {e}")
    else:
        app.state.feature_names = None
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

    # Ensure model and feature extractor are available
    model = getattr(app.state, "model", None)
    feat_module = getattr(app.state, "feature_extractor", None)

    if model is None:
        # Model not loaded; return received but indicate no prediction
        return {"status": "received", "filename": str(dest.name), "prediction": None, "note": "model not loaded"}

    if feat_module is None or not hasattr(feat_module, "extract_features"):
        raise HTTPException(status_code=500, detail="Feature extractor not available")

    # Extract features from the saved file
    try:
        features = feat_module.extract_features(str(dest))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature extraction failed: {e}")

    # Align extracted features to the training feature set (if available)
    feature_names = getattr(app.state, "feature_names", None)
    if feature_names:
        aligned: dict = {}
        # fill aligned dict according to feature_names
        for fname in feature_names:
            if fname in features:
                aligned[fname] = features[fname]
                continue

            # handle one-hot encoded emotion features like 'dominante_emotion_happy'
            if fname.startswith("dominante_emotion_"):
                base = "dominante_emotion"
                target = fname.split("dominante_emotion_")[-1]
                aligned[fname] = 1.0 if features.get(base) == target else 0.0
                continue

            # handle one-hot encoded video category features like 'video_kategorie_Comedy'
            if fname.startswith("video_kategorie_"):
                base = "video_kategorie"
                target = fname.split("video_kategorie_")[-1]
                aligned[fname] = 1.0 if features.get(base) == target else 0.0
                continue

            # default numeric fallback
            aligned[fname] = 0.0

        try:
            X = pd.DataFrame([aligned], columns=feature_names)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to prepare aligned features for model: {e}")
    else:
        # no feature list available; fall back to using whatever keys extract_features returned
        try:
            X = pd.DataFrame([features])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to prepare features for model: {e}")

    # Compute score (probability of positive class)
    score: Optional[float] = None
    try:
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X)
            # assume positive class is at index 1
            if proba.ndim == 2 and proba.shape[1] >= 2:
                score = float(proba[:, 1][0])
            else:
                score = float(proba[0])
        elif hasattr(model, "predict"):
            pred = model.predict(X)
            # If predict returns probabilities
            if isinstance(pred, (list, tuple)) or hasattr(pred, "shape"):
                val = pred[0]
                try:
                    score = float(val)
                except Exception:
                    score = 1.0 if val else 0.0
            else:
                score = float(pred)
        else:
            # fallback: unable to score
            score = None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model prediction failed: {e}")

    if score is None:
        raise HTTPException(status_code=500, detail="Model did not produce a score")

    # Clip score to [0,1]
    try:
        score = max(0.0, min(1.0, float(score)))
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid score value from model")

    label = "viral" if score >= 0.5 else "normal"

    # Persist analysis result if DB available
    try:
        if database is not None and hasattr(database, "insert_analysis"):
            try:
                database.insert_analysis(str(dest.name), score, label, None)
            except Exception as e:
                logger.warning(f"Failed to insert analysis record: {e}")
    except Exception:
        # ignore DB errors for response
        pass

    return {"filename": str(dest.name), "score": score, "label": label}


if __name__ == "__main__":
    # Optional development server start (uvicorn may or may not be installed)
    try:
        import uvicorn

        uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
    except Exception:
        print("uvicorn not available - run the app with an ASGI server of your choice")
