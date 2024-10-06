# Use Python 3.12.5 slim image as the base
FROM python:3.12.5-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock* ./

# Project initialization
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the project
COPY src ./src

# Include the project in the Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Copy environment variables
COPY .env ./.env

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["poetry", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]