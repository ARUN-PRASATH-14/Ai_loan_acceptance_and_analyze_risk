FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PORT=7860 \
    HOME=/app

WORKDIR /app

# Install system dependencies & Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy package files and install frontend dependencies
COPY package*.json ./
RUN npm install

# Copy python dependencies and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Build frontend bundle
RUN npm run build

# Set permissions for HuggingFace user environment (user 1000)
RUN chmod -R 777 /app

EXPOSE 7860

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:7860", "--timeout", "300", "--workers", "1"]
