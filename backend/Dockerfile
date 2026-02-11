FROM python:3.12-slim

WORKDIR /app

# Create fonts directory
RUN mkdir -p /app/fonts

# Install system dependencies for libraqm (complex text layout for Persian/Arabic) and curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    libraqm-dev \
    libfribidi-dev \
    libharfbuzz-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Reinstall Pillow with raqm support
RUN pip uninstall -y Pillow && \
    pip install --no-cache-dir Pillow~=10.4.0

# Copy application code
COPY . .

# Expose port
EXPOSE 3001

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3001"]

