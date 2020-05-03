import requests
from bs4 import BeautifulSoup as Soup


url = "https://stooq.pl/t/?i=532"
headers = {
    'User-Agent': "Praca dyplomowa"
}

r = requests.get(url, headers=headers)
soup = Soup(r.text, "html.parser")

with open('stock_data.csv', "w", encoding="utf-8") as csv_file:
    table = soup.find('tbody', {'align': 'right'})
    rows = table('tr')
    for row in rows:
        data = list()
        for col in row('td')[:3]:
            data.append(col.text.strip())
        print(data)
        data = ",".join(data) + "\n"
        csv_file.write(data)
