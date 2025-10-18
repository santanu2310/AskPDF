#!/bin/bash

# This script builds and runs the Docker container for the Celery worker.

# Build the Docker image
echo "Building the Docker image..."
docker build -t pdf-processor .

# Run the Docker container
# The --env-file flag loads environment variables from the .env file.
echo "Running the Docker container..."
docker run --env-file app/.env pdf-processor