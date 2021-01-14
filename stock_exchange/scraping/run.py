from abc import ABC, abstractmethod
from sys import argv

from scraper import StockScraper, StockHistoryScraper, NewsScraper
from writer import write_data


URL = "https://stooq.pl/t/?i=582"


class Command(ABC):

    @abstractmethod
    def execute(self) -> None:
        pass


class ScrapeDataCommand(Command):
    """
    Command to scrape new stock data from given URL
    """
    def __init__(self):
        self.data = list()
        self.output = 'stock_data.csv'

    def execute(self):
        scraper = StockScraper()
        self.data = scraper.scrape(URL)
        write_data(self.data, self.output)


class ScrapeHistoricalDataCommand(Command):
    """
    Command to scrape new stock data from given URL
    """
    def __init__(self):
        self.data = list()
        self.output = 'stock_history_data.csv'

    def execute(self):
        scraper = StockHistoryScraper()
        self.data = scraper.scrape(URL)
        write_data(self.data, self.output, join_data=False)


class NewsScraperDataCommand(Command):
    """
    Command to scrape news for all companies
    """
    def __init__(self):
        self.data = list()
        self.base_url = "https://www.biznesradar.pl/wiadomosci"
        self.output = 'stock_news.csv'
        self.STOCK_TICKERS = [
            'ACP', 'ALE', 'ALR',
            'ATT', 'CCC', 'CDR',
            'CPS', 'DNP', 'EAT',
            'ENA', 'EUR', 'ING',
            'JSW', 'KER', 'KGH',
            'KRU', 'KTY', 'LPP',
            'LTS', 'MBK', 'MIL',
            'OPL', 'PEO', 'PGE',
            'PGN', 'PKN', 'PKO',
            'PZU', 'SPL', 'TPE', 'WIG30'
        ]


    def execute(self):
        scraper = NewsScraper()
        for stock_ticker in self.STOCK_TICKERS:
            URL = f"{self.base_url}/{stock_ticker}"
            self.data += scraper.scrape(URL, stock_ticker)
        write_data(self.data, self.output, separator='|')


COMMANDS = {
    'prices': ScrapeDataCommand,
    'history': ScrapeHistoricalDataCommand,
    'news': NewsScraperDataCommand,
}


if __name__ == "__main__":
    try:
        passed_argument = argv[1]
    except IndexError:
        passed_argument = "price"
    cmd = COMMANDS.get(passed_argument, ScrapeDataCommand)()
    cmd.execute()
