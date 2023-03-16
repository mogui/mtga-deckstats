FROM python:3-alpine as base


WORKDIR /app

FROM base as builder
ENV POETRY_VERSION=1.4.0

RUN apk add --no-cache gcc libffi-dev musl-dev
RUN pip install "poetry==$POETRY_VERSION"
RUN python -m venv /venv

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt | /venv/bin/pip install -r /dev/stdin

COPY . .
RUN poetry build && /venv/bin/pip install dist/*.whl


FROM base as final

RUN apk add --no-cache libffi libpq
COPY --from=builder /venv /venv
COPY docker-entrypoint.sh ./
CMD ["./docker-entrypoint.sh"]
