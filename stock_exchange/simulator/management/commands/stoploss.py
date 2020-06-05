from django.core.management.base import BaseCommand

from simulator.models import Wallet
from simulator.utils import sell_stocks


class Command(BaseCommand):
    help = 'Sell stocks which price is below stoploss value set by user.'

    def handle(self, *args, **options):
        wallets = Wallet.objects.all()
        for wallet in wallets:
            
            if wallet.stoploss and wallet.stock.price <= wallet.stoploss:
                sell_stocks(wallet, wallet.number)
                print("sold!")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully sold stocks")
        )
