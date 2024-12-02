# Base image
FROM python:3.12-slim

LABEL maintainer="MOH"
# Set environment variables for better behavior
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /chainlit_app

# Install system dependencies
# These are minimal dependencies; modify as needed for your app.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./ /chainlit_app/

# Expose the port Chainlit will run on
EXPOSE 8100

ENV CHAINLIT_AUTH_SECRET .4=P6SnNr*P0sf~gzV>tq0*eZ7NoxeVyN50lN_%hVmxF%?wI3OUDV%0p8MsD9jrq
# Command to run Chainlit
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8100"]
