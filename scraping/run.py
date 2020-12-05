from scraper import StockScraper
from writer import write_data


class ScrapeDataCommand:
    """
    Command to scrape new stock data from given URL
    """
    def __init__(self):
        self.data = list()

    def execute(self, url, output='stock_data.csv'):
        scraper = StockScraper()
        self.data = scraper.scrape(url)
        write_data(self.data, output)


if __name__ == "__main__":
    url = "https://stooq.pl/t/?i=532"
    cmd = ScrapeDataCommand()
    cmd.execute(url)
