
FROM python:3.12-slim

# System setup, package installation, and cleanup are run in a single layer
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        gcc \
        libnetcdf-dev \
    && pip3 install --upgrade pip cython poetry \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Create user and workspace
RUN adduser --quiet --disabled-password --shell /bin/sh \
        --home /home/dockeruser --gecos "" --uid 1000 dockeruser \
    && mkdir -p /worker \
    && chown dockeruser:dockeruser /worker

# Set working directory
WORKDIR /worker

# Install dependencies as root (needed for system-level packages)
COPY pyproject.toml ./
RUN poetry config virtualenvs.create false \
    && poetry install --with harmony --without integration

# Copy application files
#   Set DIST_PATH argument if running the pip install on a local directory, so
#   the local dist files are copied into the container.
ARG DIST_PATH
COPY --chown=dockeruser:dockeruser $DIST_PATH $DIST_PATH
COPY --chown=dockeruser:dockeruser ./docker-entrypoint.sh ./
RUN chmod +x ./docker-entrypoint.sh

# Switch to non-root user for runtime
USER dockeruser
ENV HOME=/home/dockeruser \
    PYTHONPATH="/home/dockeruser/.local/bin" \
    PATH="/home/dockeruser/.local/bin:${PATH}"

# Run the service
ENTRYPOINT ["./docker-entrypoint.sh"]
