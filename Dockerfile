# Use Python slim image for smaller size
FROM python:3.11-slim

# Install system dependencies and build tools
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    build-essential \
    git \
    protobuf-compiler \
    libprotobuf-dev \
    libnl-route-3-dev \
    libnl-nf-3-dev \
    libnl-genl-3-dev \
    pkg-config \
    flex \
    bison \
    && rm -rf /var/lib/apt/lists/*

# Install nsjail from source
RUN git clone https://github.com/google/nsjail.git /tmp/nsjail && \
    cd /tmp/nsjail && \
    make && \
    cp nsjail /usr/local/bin/ && \
    chmod +x /usr/local/bin/nsjail && \
    rm -rf /tmp/nsjail

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY python.config /etc/nsjail/python.config

# Create non-root user for security
RUN useradd -m -u 1000 pythonuser && \
    chown -R pythonuser:pythonuser /app

# Switch to non-root user
USER pythonuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["python", "app.py"]
