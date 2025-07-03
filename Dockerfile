
FROM python:3.12-slim

RUN apt-get update \
     && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
    gcc \
    libnetcdf-dev \
    #libhdf5-dev \
    #hdf5-helpers \
    && pip3 install --upgrade pip \
    && pip3 install cython \
    && pip3 install poetry \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


# Create a new user
RUN adduser --quiet --disabled-password --shell /bin/sh --home /home/dockeruser --gecos "" --uid 1000 dockeruser
USER dockeruser
ENV HOME /home/dockeruser
ENV PYTHONPATH "${PYTHONPATH}:/home/dockeruser/.local/bin"
ENV PATH="/home/dockeruser/.local/bin:${PATH}"

# The 'SOURCE' argument is what will be used in 'pip install'.
ARG SOURCE

# Set this argument if running the pip install on a local directory, so
# the local dist files are copied into the container.
ARG DIST_PATH

USER root
RUN mkdir -p /worker && chown dockeruser /worker
COPY pyproject.toml /worker

WORKDIR /worker
# ENV PYTHONPATH=${PYTHONPATH}:${PWD}
COPY --chown=dockeruser $DIST_PATH $DIST_PATH
#RUN pip3 install --no-cache-dir --force --user --index-url https://pypi.org/simple/ --extra-index-url https://test.pypi.org/simple/ $SOURCE \
#    && rm -rf $DIST_PATH

#install poetry as root
RUN poetry config virtualenvs.create false
RUN poetry install --with harmony --without integration

USER dockeruser
COPY --chown=dockeruser ./docker-entrypoint.sh docker-entrypoint.sh
# Run the service
ENTRYPOINT ["./docker-entrypoint.sh"]
