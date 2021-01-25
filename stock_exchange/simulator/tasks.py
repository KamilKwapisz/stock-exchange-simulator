from celery import shared_task
from django.core.management import call_command

from scraping.run import ScrapeDataCommand, NewsScraperDataCommand


@shared_task
def apply_stoploss():
    call_command('stoploss', interactive=False)


@shared_task
def update_stock_data():
    # scraping
    cmd = ScrapeDataCommand()
    cmd.execute()

    # updating
    call_command('update', interactive=False)

    # stoploss
    apply_stoploss.delay()


@shared_task
def scrape_news():
    cmd = NewsScraperDataCommand()
    cmd.execute()
