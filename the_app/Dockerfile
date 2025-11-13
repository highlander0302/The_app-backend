FROM python:3.14-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential netcat-openbsd \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --no-ansi

ENTRYPOINT ["./the_app/entrypoint.sh"]