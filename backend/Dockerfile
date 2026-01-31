FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Download and install Vazirmatn Persian font
RUN mkdir -p /app/fonts && \
    wget -q -O /tmp/vazirmatn.zip "https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/vazirmatn-v33.003.zip" && \
    apt-get update && apt-get install -y --no-install-recommends unzip && \
    unzip -q /tmp/vazirmatn.zip -d /tmp/vazirmatn && \
    cp /tmp/vazirmatn/fonts/ttf/Vazirmatn-Regular.ttf /app/fonts/ && \
    cp /tmp/vazirmatn/fonts/ttf/Vazirmatn-Bold.ttf /app/fonts/ && \
    rm -rf /tmp/vazirmatn /tmp/vazirmatn.zip && \
    apt-get purge -y unzip && apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 3001

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3001"]

