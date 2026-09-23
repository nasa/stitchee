FROM python:3.12-slim

# Passing version
ARG SERVICE_VERSION
ENV SETUPTOOLS_SCM_PRETEND_VERSION=$SERVICE_VERSION

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
    gcc \
    libnetcdf-dev \
    && pip3 install --no-cache-dir --upgrade pip cython \
    && apt-get purge -y --auto-remove gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create a new user
RUN adduser --quiet --disabled-password --shell /bin/sh \
--home /home/dockeruser --gecos "" --uid 1000 dockeruser

RUN mkdir -p /worker && chown dockeruser /worker

WORKDIR /worker

COPY --chown=dockeruser:dockeruser pyproject.toml README.md LICENSE ./
COPY --chown=dockeruser:dockeruser stitchee ./stitchee
COPY --chown=dockeruser:dockeruser uv.lock ./
COPY --chown=dockeruser:dockeruser --chmod=755 docker-entrypoint.sh ./

USER dockeruser
RUN uv sync --frozen
RUN uv tool run hatch version

ENV HOME=/home/dockeruser
ENV PATH="/worker/.venv/bin:$PATH"

ENTRYPOINT ["./docker-entrypoint.sh"]
