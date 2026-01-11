# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using uv
RUN uv pip install --system -e .
RUN uv pip install --system -e ".[dev]"

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p data/raw data/processed data/external models reports/figures logs notebooks metrics plots params mlruns metrics plots params mlruns

# Expose Jupyter and MLflow ports
EXPOSE 8888 5000

# Default command
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
