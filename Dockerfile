# Simple Dockerfile for OCR service
# - Installs system Tesseract and Kiswahili language pack
# - Installs Python dependencies from requirements.txt

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV TESSERACT_CMD=/usr/bin/tesseract

# Install Tesseract and minimal runtime libs required by opencv
#RUN apt-get update \
#    && apt-get install -y --no-install-recommends \
#        tesseract-ocr \
#        tesseract-ocr-swa \
#        libgl1 libglib2.0-0 libsm6 libxrender1 libxext6 ca-certificates \
#    && rm -rf /var/lib/apt/lists/*

#WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

EXPOSE 8090

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090"]
