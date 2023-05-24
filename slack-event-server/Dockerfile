FROM python:3.11 as base
ENV TZ=Asia/Tokyo \
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

COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install

WORKDIR /app/slack-event-server

CMD python genieslack/main.py
