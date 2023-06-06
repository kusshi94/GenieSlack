FROM python:3.11 as base
ENV TZ=Asia/Tokyo \
    \
    PYTHONUNBUFFERED=1 \
    \
    POETRY_VERSION=1.4.0 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

ENV PATH="$POETRY_HOME/bin:$PATH"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        curl \
        build-essential \
        git  && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /tmp/esa-oauth-server
COPY ./esa-oauth-server/pyproject.toml ./esa-oauth-server/poetry.lock ./
COPY ./dbmgr/ ../dbmgr/
RUN poetry lock
RUN poetry install --only main --no-root

WORKDIR /app/esa-oauth-server

CMD ["/bin/bash", "-c", "poetry install --only main && gunicorn -w 4 -b 0.0.0.0:5000 'esa_oauth_server.app:app'"]
