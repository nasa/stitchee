
FROM python:3.12-slim

# System setup, package installation, and cleanup are run in a single layer
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        gcc \
        libnetcdf-dev \
    && pip3 install --upgrade pip cython uv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create user and workspace
RUN adduser --quiet --disabled-password --shell /bin/sh \
        --home /home/dockeruser --gecos "" --uid 1000 dockeruser \
    && mkdir -p /worker \
    && chown dockeruser:dockeruser /worker

# Set working directory
WORKDIR /worker

# Copy project files and install (as root for system-wide installation)
COPY pyproject.toml README.md LICENSE ./
COPY stitchee/ ./stitchee/
RUN uv sync --extra dev --extra harmony

# Copy and prepare entrypoint
COPY docker-entrypoint.sh ./
RUN chmod +x ./docker-entrypoint.sh \
    && chown dockeruser:dockeruser ./docker-entrypoint.sh

# Switch to non-root user for runtime
USER dockeruser
ENV HOME=/home/dockeruser \
    PYTHONPATH="/worker"

ENTRYPOINT ["./docker-entrypoint.sh"]
