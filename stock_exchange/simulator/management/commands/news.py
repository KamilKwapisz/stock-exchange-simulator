from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from simulator.models import Stock, News
from simulator.utils import save_stock_history


class Command(BaseCommand):
    help = 'Update news from file'

    def add_arguments(self, parser):
        DEFAULT_FILENAME = "stock_news.csv"
        parser.add_argument('filename', type=str, nargs='?', default=DEFAULT_FILENAME)

    def handle(self, *args, **options):
        news_data = self.__read_file(options['filename'])
        for row in news_data:
            row = row.rstrip()
            try:
                short_name, title, link, text, portal, date = row.split("|")
            except ValueError:
                continue
            try:
                dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise CommandError(r"Niepoprawny format daty. Wymagany format: %Y-%m-%d %H:%M:%S")
            else:
                stock = Stock.objects.get(short_name=short_name)
                News.objects.create(
                    stock=stock,
                    title=title,
                    timestamp=dt,
                    link=link,
                    text=text,
                    portal=portal
                )

        self.stdout.write(self.style.SUCCESS(f"Successfully loaded {len(news_data)} news"))

    def __read_file(self, filename):
        try:
            with open(filename, "r", encoding='utf-8') as reader:
                data = reader.readlines()
        except FileNotFoundError:
            raise CommandError(f"Brak pliku o nazwie {filename}.")
        else:
            return data
