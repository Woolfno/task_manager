FROM python:3.12-alpine

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache gcc python3-dev libc-dev linux-headers
RUN apk add postgresql-client build-base postgresql-dev

COPY pyproject.toml ./

RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --without dev\
    && rm -rf $(poetry config cache-dir)/{cache,artifacts}

COPY ./ ./
