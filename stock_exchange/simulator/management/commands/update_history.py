from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.timezone import get_current_timezone

from simulator.models import Stock
from simulator.utils import save_stock_history


class Command(BaseCommand):
    help = 'Update stock historical data'

    def add_arguments(self, parser):
        DEFAULT_FILENAME = "stock_history_data.csv"
        parser.add_argument('filename', type=str, nargs='?', default=DEFAULT_FILENAME)

    def handle(self, *args, **options):
        stock_data = self.__read_file(options['filename'])
        latest_price = 0.0
        counter = 0
        for row in stock_data:
            try:
                ticker_symbol = row.get('short_name')
                stock = Stock.objects.get(short_name=ticker_symbol.upper())
            except Stock.DoesNotExist:
                print(ticker_symbol)
                continue
            else:
                stock.price = row.get('price')
                stock.timestamp = datetime.strptime(row.get('datetime'), "%Y-%m-%d")
                save_stock_history(stock)
                counter += 1
                print(counter)

        self.stdout.write(self.style.SUCCESS(f"Successfully updated {counter} stock data in history"))

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
            short_name, date, price = row.split(",")
            try:
                price = float(price)
            except ValueError:
                raise CommandError(f"Niepoprawny format ceny akcji.")
            else:
                stock_details = {
                    'datetime': date,
                    'short_name': short_name,
                    'price': price
                }
                stock_data.append(stock_details)
        return stock_data
