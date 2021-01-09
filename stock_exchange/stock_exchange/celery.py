import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_exchange.settings')

app = Celery('stock_exchange')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_schedule = {
    'regular-stock-data-scraping': {
        'task': 'simulator.tasks.update_stock_data',
        'schedule': crontab(minute=0, hour='*/3'),
    },
    'regular-news-scraping': {
        'task': 'simulator.tasks.scrape_news',
        'schedule': crontab(day='*/1'),
    },
}
