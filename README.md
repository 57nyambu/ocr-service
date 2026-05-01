OCR Identity Verification Service
=================================

This microservice extracts text from credential images (IDs, passports, certificates) using Tesseract OCR via `pytesseract`.

This README contains everything needed to run the service on Windows and Linux, including platform-specific notes about the Tesseract binary.

Requirements
------------
- Python 3.10+ (3.11 recommended)
- System Tesseract OCR (binary) installed
- A Python virtual environment (recommended)

Install system Tesseract
------------------------
Windows
- Download and install the official Tesseract installer from: https://github.com/tesseract-ocr/tesseract/releases
- Default install path is typically:
  `C:\Program Files\Tesseract-OCR\tesseract.exe`
- For the current PowerShell session you can set the explicit path the app will use:

```powershell
$env:TESSERACT_CMD = 'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

- To set it permanently for your user, run (from an elevated prompt if needed):

```powershell
setx TESSERACT_CMD "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install -y tesseract-ocr
# for additional languages (e.g., Kiswahili) install language packs if available
sudo apt install -y tesseract-ocr-swa
```

macOS (Homebrew)

```bash
brew install tesseract
```

Python dependencies
-------------------
From the project root (where `requirements.txt` is located):

```bash
python -m venv venv
# Windows (PowerShell)
venv\Scripts\Activate.ps1
# Linux / macOS
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

Run the service
---------------
Start the FastAPI app with Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8090
```

Example requests
----------------
PowerShell (use `curl.exe` to avoid the PowerShell alias for `curl`):

```powershell
curl.exe -X POST "http://localhost:8090/ocr" -F "file=@C:\path\to\document.jpg"
```

Bash / Linux / macOS:

```bash
curl -X POST http://localhost:8090/ocr -F "file=@/path/to/document.jpg"
```

Or use `http` or `jq` to pretty-print responses.

Common issues & troubleshooting
-------------------------------
- Error: "tesseract is not installed or it's not in your PATH"
  - Confirm Tesseract is installed by running:

```bash
# Windows (PowerShell)
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --version

# Linux / macOS
tesseract --version
```

  - If the command above works but the app still complains, set `TESSERACT_CMD` (Windows) or ensure the `tesseract` binary is on `PATH`.

- PowerShell `curl` syntax / bad hostname errors:
  - Use `curl.exe` or use `Invoke-RestMethod` / `Invoke-WebRequest`.
  - Avoid using a trailing backtick incorrectly; keep the whole command on one line or use the backtick as a line-continuation at the end of the line.

Notes for developers
--------------------
- The code expects a system Tesseract binary. The `pytesseract` package is a wrapper and does not include the binary.
- On Windows: you can set `TESSERACT_CMD` to the full `tesseract.exe` path to override PATH-based discovery for the current session.
- The OCR module attempts to detect when Tesseract is unavailable and raises a clear error advising the above fixes.

Files of interest
-----------------
- main.py — FastAPI entrypoint and HTTP routes
- ocr.py — image preprocessing and OCR logic
- requirements.txt — Python dependencies

Contact / help
--------------
If you run into issues not covered here, paste the server log and the exact command you used to run the client request.
