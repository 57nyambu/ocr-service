"""
main.py — OCR microservice entry point.
Run:  gunicorn main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8090
Dev:  uvicorn main:app --host 0.0.0.0 --port 8090 --reload
"""

import logging

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ocr import extract_text, OCRError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="OCR Identity Verification Service",
    description=(
        "Extracts text from credential images (IDs, passports, certificates). "
        "Supports English and Kiswahili."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/bmp", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    """Quick liveness check."""
    return {"status": "ok"}


@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    """
    Upload a credential image and receive extracted text.

    - **file**: JPEG / PNG / BMP / WebP image of the document
    - Returns extracted text, confidence score, and any quality warnings.
    """
    # --- Validate content type ---
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=(
                f"Unsupported file type: '{file.content_type}'. "
                f"Accepted: {', '.join(sorted(ALLOWED_TYPES))}."
            ),
        )

    # --- Read and size-check ---
    img_bytes = await file.read()
    if len(img_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is {MAX_FILE_SIZE // (1024*1024)} MB.",
        )

    if len(img_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # --- Run OCR ---
    try:
        result = extract_text(img_bytes)
    except OCRError as e:
        # Predictable image-quality errors → 422 (client can fix these)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        logger.exception("OCR processing failed for file: %s", file.filename)
        raise HTTPException(status_code=500, detail="OCR processing failed. Check server logs.")

    return JSONResponse(content={
        "filename": file.filename,
        **result,
    })
