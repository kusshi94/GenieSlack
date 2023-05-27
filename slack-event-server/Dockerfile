FROM python:3.11
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

WORKDIR /tmp
COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --only main --no-root

WORKDIR /app/genieslack

CMD ["/bin/bash", "-c", "poetry install --only main && python genieslack/main.py.py"]
