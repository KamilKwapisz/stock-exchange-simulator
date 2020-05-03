from scraper import StockScraper
from writer import write_data

url = "https://stooq.pl/t/?i=532"

scraper = StockScraper()
data = scraper.scrape(url)
write_data(data)
