from celery import Celery

celery_app = Celery('crawler')

celery_app.config_from_object('celery_config')

celery_app.conf.task_routes = {
    'tasks.fetch_and_save_html': {'queue': 'crawler'},
    'tasks.parse_and_discover_links': {'queue': 'parser'}
}

from app import tasks
