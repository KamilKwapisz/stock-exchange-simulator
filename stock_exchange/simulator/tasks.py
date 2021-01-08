from celery import shared_task
from django.core.management import call_command

from scraping.run import ScrapeDataCommand


@shared_task
def update_stock_data():
    # scraping
    cmd = ScrapeDataCommand()
    cmd.execute()

    # updating
    call_command('update', interactive=False)
