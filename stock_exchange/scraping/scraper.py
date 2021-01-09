import requests
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep
from urllib.parse import urljoin, urlparse

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

    def get_wig30_data(self) -> list:
        self.URL = "https://stooq.pl/q/?s=wig30"
        html = self.__get()
        soup = BeautifulSoup(html, self.parser)
        price = soup.find('span', {'id': 'aq_wig30_c2'}).text
        return ["WIG30", "WIG30", price]

    def scrape(self, URL: str) -> list:
        self.URL = URL
        html = self.__get()
        data = self.parse(html)
        wig30_data = self.get_wig30_data()
        print(data)
        print(wig30_data)
        data.append(wig30_data)
        return data


class StockHistoryScraper:
    def __init__(self):
        self.URL: str
        self.ua = "Praca dyplomowa"
        self.response = None
        self.parser = "html.parser"

    def __get(self, url: str, extract_html=False) -> str:
        headers = {
            'User-Agent': self.ua
        }
        response = requests.get(
            url=url,
            headers=headers
        )
        if extract_html is True:
            html = response.text
            return html
        else:
            return response

    @staticmethod
    def __join_url(base_url: str, link: str) -> str:
        parsed_url = urlparse(base_url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        url = urljoin(domain, link)
        return url

    def get_stock_data_links(self, soup) -> list:
        links = soup.select("tr[id^='r_'] > td > b > a")
        data_urls = list()
        for link in links:
            link = link.get('href')
            url = self.__join_url(self.URL, link)
            data_urls.append(url)
        data_urls.append('https://stooq.pl/q/?s=wig30')
        return data_urls

    def get_historical_data(self, url: str):
        parsed = urlparse(url)
        historical_data_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}/d/l/?{parsed.query}&d1=20150101&d2={datetime.now().strftime('%Y%m%d')}&i=d"
        print('LINK, ', historical_data_url)
        ticker_symbol = parsed.query.split('=')[-1]
        csv_data = self.__get(historical_data_url, extract_html=True)
        data = self.parse_data(csv_data, ticker_symbol)
        return data

    def parse_data(self, csv_data: str, ticker_symbol: str):
        data = list()
        rows = csv_data.split()[1:]
        # print("ROWS", len(rows), rows[:5])
        for row in rows:
            row = row.strip()
            elements = row.split(',')

            try:
                new_data = [
                    ticker_symbol,
                    elements[0],
                    elements[-2]
                ]
            except IndexError:
                print("ERROR", elements, row)
                continue
            new_data = ','.join(new_data) + "\n"
            data.append(new_data)
        return data


    def scrape(self, URL: str) -> list:
        self.URL = URL
        html = self.__get(URL, extract_html=True)
        soup = BeautifulSoup(html, self.parser)
        stock_data_links = self.get_stock_data_links(soup)
        data = list()
        for link in stock_data_links:
            print(link)
            row_data = self.get_historical_data(link)
            data += row_data
            sleep(2)
        return data


class NewsScraper:
    def __init__(self):
        self.URL: str
        self.ua = "Praca dyplomowa"
        self.response = None
        self.parser = "html.parser"

    def __get(self, url: str, extract_html=False) -> str:
        headers = {
            'User-Agent': self.ua
        }
        response = requests.get(
            url=url,
            headers=headers
        )
        if extract_html is True:
            html = response.text
            return html
        else:
            return response

    def get_news(self, soup, stock_ticker: str) -> list:
        all_news = soup('div', {'class': "record-type-NEWS"})
        news_data = list()
        for news in all_news:
            a_tag = news.select_one('div.record-header > a')
            title = a_tag.text
            print(title)
            link = a_tag.get('href')
            text = news.select_one('div.record-body').text.strip()
            portal = news.select_one('a.record-author').text
            date = news.select_one('span.record-date').text
            news_data.append(
                (stock_ticker, title, link, text, portal, date)
            )
        return news_data

    def scrape(self, URL: str, stock_ticker: str) -> list:
        self.URL = URL
        html = self.__get(URL, extract_html=True)
        soup = BeautifulSoup(html, self.parser)
        news_data = self.get_news(soup, stock_ticker)
        return news_data
