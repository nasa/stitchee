
FROM python:3.12-slim

# System setup, package installation, and cleanup are run in a single layer
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        gcc \
        libnetcdf-dev \
    && pip3 install --upgrade pip cython poetry \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Create non-root user with proper environment
RUN adduser --quiet --disabled-password --shell /bin/sh \
        --home /home/dockeruser --gecos "" --uid 1000 dockeruser \
    && mkdir -p /worker \
    && chown dockeruser /worker

# Switch to non-root user and set environment
USER dockeruser
ENV HOME=/home/dockeruser \
    PYTHONPATH="/home/dockeruser/.local/bin" \
    PATH="/home/dockeruser/.local/bin:${PATH}"

# Build arguments
# The 'SOURCE' argument is what will be used in 'pip install'.
ARG SOURCE
# Set this argument if running the pip install on a local directory, so
# the local dist files are copied into the container.
ARG DIST_PATH

# Set working directory and copy dependency files
WORKDIR /worker
COPY --chown=dockeruser pyproject.toml ./

# Configure poetry and install dependencies as root (if needed for system packages)
USER root
RUN poetry config virtualenvs.create false
RUN poetry install --with harmony --without integration

# Copy remaining files and switch back to non-root user
COPY --chown=dockeruser $DIST_PATH $DIST_PATH
COPY --chown=dockeruser ./docker-entrypoint.sh ./
USER dockeruser

# Run the service
ENTRYPOINT ["./docker-entrypoint.sh"]
