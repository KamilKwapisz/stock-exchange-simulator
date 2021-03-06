from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from simulator.models import Stock
from simulator.utils import save_stock_history


class Command(BaseCommand):
    help = 'Update stock data'

    def add_arguments(self, parser):
        DEFAULT_FILENAME = "stock_data.csv"
        parser.add_argument('filename', type=str, nargs='?', default=DEFAULT_FILENAME)

    def handle(self, *args, **options):
        stock_data = self.__read_file(options['filename'])
        latest_price = 0.0
        for row in stock_data:
            try:
                company_name = row.get('name')
                stock = Stock.objects.get(name=company_name)
                latest_price = stock.price
            except Stock.DoesNotExist:
                stock = Stock.objects.create(
                    name=company_name,
                    short_name=row.get('short_name'),
                    price=row.get('price'),
                    tendention='up',
                    timestamp=timezone.now()
                )
            else:
                stock.price = row.get('price')
                stock.tendention = 'up' if stock.price > latest_price else 'down'
            finally:
                stock.save()
                save_stock_history(stock)

        self.stdout.write(self.style.SUCCESS(f"Successfully updated {len(stock_data)} stock data"))

    def __read_file(self, filename):
        try:
            with open(filename, "r", encoding='utf-8') as reader:
                data = reader.readlines()
        except FileNotFoundError:
            raise CommandError(f"Brak pliku o nazwie {filename}.")
        else:
            parsed_stock_data = self.__parse_data(data)
            return parsed_stock_data
    
    def __parse_data(self, data):
        stock_data = list()
        for row in data:
            row = row.rstrip()
            short_name, name, price = row.split(",")
            try:
                price = float(price)
            except ValueError:
                raise CommandError(f"Niepoprawny format ceny akcji.")
            else:
                stock_details = {
                    'name': name,
                    'short_name': short_name,
                    'price': price
                }
                stock_data.append(stock_details)
        return stock_data
