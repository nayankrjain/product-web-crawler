# Web Crawler

Crawls product urls from different websites

## Installation

Using poetry for package management

```bash
pip install poetry
poetry install # will install packages
poetry shell # will activate shell environment
```

## Usage
Start docker containers

```bash
# This will start rabbitmq and mongodb
docker-compose -f docker-compose.yml up
```

Start Celery Workers
```bash
# start celery Fetcher worker
celery -A celery_app worker --loglevel=info -Q crawler --concurrency=1 -n fetcher
```
```bash
# start celery parser worker
celery -A celery_app worker --loglevel=info -Q parser -n parser_worker --concurrency=1
```

```python
# run the script to start fetching product urls
python run.py
```

```python
# run this script to see all fetched product urls"
python products.py
```

