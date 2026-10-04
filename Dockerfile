FROM python:3.14-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# CPU-only PyTorch first: much smaller than the default GPU version
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install dependencies before copying code, so code changes don't trigger a full reinstall
COPY requirements.txt .
RUN pip install -r requirements.txt

# Download the embedding model at build time, not every time the container starts
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY *.py ./

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]