# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /pdf_classification


# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Functions Framework
RUN pip install functions-framework

# Copy the function code into the container
COPY . .

# Set the environment variable for Google Cloud credentials
ENV GOOGLE_APPLICATION_CREDENTIALS=/pdf_classification/sa_gcs.json

# Set the environment variable for the function name
ENV FUNCTION_TARGET=validate_and_classify_pdf

# Add debug echo statements
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'echo "Starting container..."' >> /entrypoint.sh && \
    echo 'echo "FUNCTION_TARGET is set to: $FUNCTION_TARGET"' >> /entrypoint.sh && \
    echo 'echo "Contents of /audio_compress:"' >> /entrypoint.sh && \
    echo 'ls -la /audio_compress' >> /entrypoint.sh && \
    echo 'echo "Starting Functions Framework..."' >> /entrypoint.sh && \
    echo 'functions-framework --target=${FUNCTION_TARGET} --debug' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Start the function
CMD ["/entrypoint.sh"]
