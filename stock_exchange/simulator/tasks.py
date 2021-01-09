from celery import shared_task
from django.core.management import call_command

from simulator.models import Stock
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
    ticker_symbols = list()
    stocks = Stock.objects.all().values('short_name')
    for stock in stocks:
        ticker_symbols.append(stock.get('short_name'))
    cmd = NewsScraperDataCommand()
    cmd.execute(ticker_symbols)
