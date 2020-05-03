import requests
from bs4 import BeautifulSoup


class StockScraper:

    def __init__(self):
        self.URL: str
        self.ua = "Praca dyplomowa"
        self.response = None
        self.parser = "html.parser"

    def __get(self) -> str:
        headers = {
            'User-Agent': self.ua
        }
        self.response = requests.get(
            url=self.URL,
            headers=headers
        )
        html = self.response.text
        return html

    def parse(self, html: str) -> list:
        data = list()
        soup = BeautifulSoup(html, self.parser)
        table = soup.find('tbody', {'align': 'right'})

        for row in table('tr'):
            cells = row('td')[:3]
            company_data = [cell.text for cell in cells]
            data.append(company_data)

        return data

    def scrape(self, URL: str) -> list:
        self.URL = URL
        html = self.__get()
        data = self.parse(html)
        return data
