import requests
from bs4 import BeautifulSoup as Soup


url = "https://stooq.pl/t/?i=532"
headers = {
    'User-Agent': "Praca dyplomowa"
}

r = requests.get(url, headers=headers)
soup = Soup(r.text, "html.parser")

table = soup.find('tbody', {'align': 'right'})
rows = table('tr')
for row in rows[:2]:
    for col in row('td')[:3]:
        print(col.text.strip())
