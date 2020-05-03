import requests
from bs4 import BeautifulSoup as Soup


url = "https://stooq.pl/t/?i=532"
headers = {
    'User-Agent': "Praca dyplomowa"
}

r = requests.get(url, headers=headers)
soup = Soup(r.text, "html.parser")
table = soup.find('tbody', {'align': 'right'})

with open('stock_data.csv', "w", encoding="utf-8") as csv_file:
    for row in table('tr'):
        cells = row('td')[:3]
        data = [cell.text for cell in cells]

        file_row = ",".join(data) + "\n"
        csv_file.write(file_row)
