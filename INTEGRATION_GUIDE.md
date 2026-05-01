Integration Guide — OCR Identity Verification Service
=====================================================

Base URL
--------
Production base URL:

https://ocr.lipana.co

Endpoints
---------
Health check:

GET /health

OCR request:

POST /ocr

Request format
--------------
- Content type: multipart/form-data
- Field name: file
- Supported formats: JPEG, PNG, BMP, WebP
- Max file size: 10 MB

Required payload (multipart form)
---------------------------------
- Endpoint: POST /ocr
- Form field: file (single image file)
- Headers: Let the client set Content-Type and boundary automatically for multipart/form-data
- Size limit: 10 MB

Expected response body
----------------------
The server always returns JSON with these fields:
- filename: string (original file name)
- success: boolean
- text: string or null
- confidence: number (0-100)
- language: string (e.g., eng+swa)
- warning: string or null (present when confidence is low)
- error: string (present when success is false)

Behavior details
----------------
- If text is not readable, the response is still 200 with success=false and error set.
- Image quality issues that block OCR return 422.
- Unsupported file type returns 415.
- Empty file returns 400.
- File too large returns 413.
- Unexpected server errors return 500.

HTTP status codes
-----------------
- 200: Request processed (success or no-text result in body)
- 400: Empty file
- 413: File too large
- 415: Unsupported file type
- 422: Image quality or OCR validation error
- 500: Unexpected server error

Recommended client behavior
---------------------------
- Set a timeout (30–60 seconds) for upload + OCR processing.
- Retry on transient failures (502/503/504 or network errors).
- Do not retry on 4xx errors; those require client-side fixes.
- Log the full response body for debugging failed OCR runs.

React / Next integration notes (no code)
----------------------------------------
- Use a multipart form upload with a single field named file.
- Do not JSON-encode the file or manually set the multipart boundary.
- If proxying through a Next API route, ensure it forwards multipart data and does not try to parse it as JSON.
- Validate file type and size on the client before upload to reduce failed requests.

Security and privacy
--------------------
- The service is HTTPS-only.
- Avoid sending sensitive documents unless required by your workflow.
- If you need authentication, add a proxy or gateway in front of the service.

Support
-------
If you need changes (rate limits, authentication, new languages), share your use case and expected request volume.
