from sys import argv

from scraper import StockScraper, StockHistoryScraper, NewsScraper
from writer import write_data


URL = "https://stooq.pl/t/?i=582"
STOCK_TICKERS = [
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
        write_data(self.data, output, join_data=False)


class NewsScraperDataCommand:
    """
    Command to scrape news for all companies
    """
    def __init__(self):
        self.data = list()
        self.base_url = "https://www.biznesradar.pl/wiadomosci"

    def execute(self, stock_tickers: list, output='stock_news.csv') -> list:
        scraper = NewsScraper()
        for stock_ticker in stock_tickers:
            URL = f"{self.base_url}/{stock_ticker}"
            self.data += scraper.scrape(URL, stock_ticker)
        write_data(self.data, output, separator='|')


if __name__ == "__main__":
    if argv[1] == 'history':
        output = "stock_history_data.csv"
        cmd = ScrapeHistoricalDataCommand()
        cmd.execute()
    elif argv[1] == 'news':
        cmd = NewsScraperDataCommand()
        cmd.execute(STOCK_TICKERS)
    else:
        output = 'stock_data.csv'
        cmd = ScrapeDataCommand()
        cmd.execute()
