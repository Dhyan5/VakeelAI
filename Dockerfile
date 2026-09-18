# Hugging Face Spaces Dockerfile for VakeelAI Legal RAG Platform Backend
FROM python:3.12-slim

# Install system dependencies including Tesseract OCR for document processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-hin \
    tesseract-ocr-kan \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirement list and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the Hugging Face sentence transformer model during build to reduce cold start latency
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

# Copy full application codebase
COPY . .

# Expose Hugging Face Spaces default port 7860
EXPOSE 7860

# Run FastAPI backend via Uvicorn on 0.0.0.0:7860
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
