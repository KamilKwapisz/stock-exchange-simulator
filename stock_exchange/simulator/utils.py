from django.conf import settings
from djmoney.money import Money

from .models import Wallet


def save_wallets(account, stock, number):
    for wallet in account.wallets.all():
        if wallet.stock == stock:
            wallet.number += number
            wallet.save()
            break
    else:
        wallet = Wallet(stock=stock, number=number)
        wallet.save()
        account.wallets.add(wallet)
        account.save()


def calculate_fee(amount):
    MINIMAL_FEE = float(getattr(settings, "MINIMAL_FEE", None))
    PERCENTAGE_FEE = int(getattr(settings, "PERCENTAGE_FEE", None))

    fee = amount * (PERCENTAGE_FEE / 100)
    if fee < MINIMAL_FEE:
        fee = MINIMAL_FEE
    
    return Money(fee, "PLN")
