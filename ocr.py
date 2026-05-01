"""
ocr.py — Image preprocessing and text extraction.
Handles credential images in English and Kiswahili.
"""

import os
import shutil

import cv2
import numpy as np
import pytesseract
from PIL import Image


# Tesseract language config: English + Kiswahili, both OCR modes
TESS_CONFIG = r"--oem 3 --psm 6"
TESS_LANG = "eng+swa"

# Minimum confidence score below which we flag the result as low-quality
MIN_CONFIDENCE = 40

# If the preprocessed image is too small, OCR quality degrades sharply
MIN_DIMENSION = 100


class OCRError(Exception):
    """Raised when OCR cannot proceed due to image issues."""
    pass


# Allow explicit Tesseract path via env var (useful on Windows)
_tess_cmd = os.getenv("TESSERACT_CMD") or os.getenv("TESSERACT_PATH")
if _tess_cmd:
    pytesseract.pytesseract.tesseract_cmd = _tess_cmd


def _ensure_tesseract() -> None:
    """Raise a clear error when the Tesseract binary cannot be found."""
    if shutil.which(pytesseract.pytesseract.tesseract_cmd):
        return
    raise OCRError(
        "Tesseract OCR is not installed or is not on PATH. "
        "Install it, then either add it to PATH or set TESSERACT_CMD."
    )


def _preprocess(img_bytes: bytes) -> np.ndarray:
    """
    Decode and clean up an image for OCR.
    Steps: decode → grayscale → denoise → threshold → (optional) deskew.
    """
    arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if img is None:
        raise OCRError("Image could not be decoded. Upload a valid JPEG, PNG, or BMP file.")

    h, w = img.shape[:2]
    if h < MIN_DIMENSION or w < MIN_DIMENSION:
        raise OCRError(
            f"Image is too small ({w}×{h} px). "
            "Please upload a clearer, higher-resolution photo."
        )

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Mild denoising — preserves thin text strokes
    denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)

    # Adaptive threshold — handles uneven lighting common in phone photos of IDs
    binary = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=31,
        C=10,
    )

    return binary


def _assess_quality(data: dict) -> float:
    """
    Return mean confidence of words that Tesseract actually recognised.
    Words with conf == -1 are layout blocks (ignored).
    """
    confs = [int(c) for c in data["conf"] if int(c) != -1]
    if not confs:
        return 0.0
    return sum(confs) / len(confs)


def extract_text(img_bytes: bytes) -> dict:
    """
    Main entry point.
    Returns a dict with:
        text        — full extracted string
        confidence  — mean OCR confidence (0-100)
        language    — languages attempted
        warning     — set when image quality is marginal
    """
    _ensure_tesseract()
    processed = _preprocess(img_bytes)

    # pytesseract needs a PIL image or a path
    pil_img = Image.fromarray(processed)

    # Get full data for confidence scoring
    data = pytesseract.image_to_data(
        pil_img,
        lang=TESS_LANG,
        config=TESS_CONFIG,
        output_type=pytesseract.Output.DICT,
    )

    confidence = _assess_quality(data)

    # Rebuild text from words (skips empty / noise tokens)
    words = [
        w for w, c in zip(data["text"], data["conf"])
        if w.strip() and int(c) != -1
    ]
    text = " ".join(words).strip()

    if not text:
        return {
            "success": False,
            "text": None,
            "confidence": round(confidence, 1),
            "language": TESS_LANG,
            "error": (
                "No readable text found. "
                "Ensure the document is flat, well-lit, and in focus."
            ),
        }

    result = {
        "success": True,
        "text": text,
        "confidence": round(confidence, 1),
        "language": TESS_LANG,
        "warning": None,
    }

    if confidence < MIN_CONFIDENCE:
        result["warning"] = (
            f"Low confidence ({confidence:.0f}/100). "
            "Results may be inaccurate — retake with better lighting and focus."
        )

    return result
