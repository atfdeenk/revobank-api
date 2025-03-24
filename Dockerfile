# Use Python 3.11.11 slim as base
FROM python:3.11.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv and create virtual environment
RUN pip install uv && \
    uv venv

# Activate virtual environment and install dependencies
COPY requirements.txt .
RUN . .venv/bin/activate && \
    uv pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE $PORT

# Start the application with gunicorn (using JSON array format)
CMD ["/app/.venv/bin/gunicorn", "--bind", "0.0.0.0:8000", "run:app"]
