FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
# Python and pip behavior to make the container cleaner, faster, and more predictable.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
# For the OS
# installing packages at the operating system level inside the container.
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
# Context is ./backend, so paths are relative to that
COPY requirements.txt requirements-dev.txt ./

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy application code
# This copies everything from backend/ folder
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/models /app/datasets

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run the application
# Uvicorn = server that runs async Python web apps
# Needed for frameworks like FastAPI 
# Handles HTTP requests efficiently and supports async code
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]