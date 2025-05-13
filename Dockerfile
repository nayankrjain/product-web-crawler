FROM python:3.11

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy the Poetry configuration files (pyproject.toml and poetry.lock)
COPY pyproject.toml poetry.lock /app/

# Install dependencies using Poetry
RUN poetry install --no-interaction --no-root

# Now copy the rest of the project
COPY .. /app/

CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info", "-Q", "crawler"]

