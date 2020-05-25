from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Scrape stock data'

    def add_arguments(self, parser):
        DEFAULT_URL = "https://stooq.pl/t/?i=532"
        parser.add_argument('url', type=str, nargs='?', default=DEFAULT_URL)

    def handle(self, *args, **options):
        url = options['url']
        self.stdout.write(self.style.SUCCESS(f"URL: {url}"))
        # for poll_id in options['poll_ids']:
        #     try:
        #         poll = Poll.objects.get(pk=poll_id)
        #     except Poll.DoesNotExist:
        #         raise CommandError('Poll "%s" does not exist' % poll_id)

        #     poll.opened = False
        #     poll.save()

        #     self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))