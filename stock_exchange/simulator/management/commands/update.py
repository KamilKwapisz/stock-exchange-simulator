from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Update stock data'

    def add_arguments(self, parser):
        DEFAULT_FILENAME = "stock_data.csv"
        parser.add_argument('filename', type=str, nargs='?', default=DEFAULT_FILENAME)

    def handle(self, *args, **options):
        data = self.__read_file()
        print(data)
        self.stdout.write(self.style.SUCCESS(f"filename: {filename}"))


    def __read_file(self):
        filename = options['filename']
        try:
            with open(filename, "r", encoding='utf-8') as reader:
                data = reader.readlines()
        except FileNotFoundError:
            raise CommandError(f"Brak pliku o nazwie {filename}")
        else:
            return data