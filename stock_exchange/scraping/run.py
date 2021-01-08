from sys import argv

from scraper import StockScraper, StockHistoryScraper
from writer import write_data


URL = "https://stooq.pl/t/?i=582"


class ScrapeDataCommand:
    """
    Command to scrape new stock data from given URL
    """
    def __init__(self):
        self.data = list()

    def execute(self, url=URL, output='stock_data.csv'):
        scraper = StockScraper()
        self.data = scraper.scrape(url)
        write_data(self.data, output)


class ScrapeHistoricalDataCommand:
    """
    Command to scrape new stock data from given URL
    """
    def __init__(self):
        self.data = list()

    def execute(self, url=URL, output='stock_history_data.csv'):
        scraper = StockHistoryScraper()
        self.data = scraper.scrape(url)
        write_data(self.data, output, historical=True)


if __name__ == "__main__":
    if argv[1] == 'history':
        output = "stock_history_data.csv"
        cmd = ScrapeHistoricalDataCommand()
    else:
        output = 'stock_data.csv'
        cmd = ScrapeDataCommand()
    cmd.execute()
