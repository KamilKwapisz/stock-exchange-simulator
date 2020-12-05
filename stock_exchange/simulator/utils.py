from django.conf import settings
from djmoney.money import Money

from .models import Wallet, StockHistory


def save_wallets(account, stock, number, stoploss):
    for wallet in account.wallets.all():
        if wallet.stock == stock:
            wallet.number += number
            wallet.stoploss = stoploss
            wallet.save()
            break
    else:
        wallet = Wallet(stock=stock, number=number, stoploss=stoploss)
        wallet.save()
        account.wallets.add(wallet)
        account.save()


def calculate_fee(amount):
    MINIMAL_FEE = Money(float(getattr(settings, "MINIMAL_FEE", None)), 'PLN')
    PERCENTAGE_FEE = int(getattr(settings, "PERCENTAGE_FEE", None))

    fee = amount * (PERCENTAGE_FEE / 100)
    if fee < MINIMAL_FEE:
        fee = MINIMAL_FEE
    else:
        fee = Money(fee, "PLN")
    
    return fee


def save_stock_history(stock):
    stockHistory = StockHistory(
        stock=stock,
        timestamp=stock.timestamp,
        price=stock.price
    )
    stockHistory.save()


def sell_stocks(wallet, number):
    wallet.number -= number
    
    if wallet.number == 0:
        wallet.delete()
    elif wallet.number < 0:
        raise ValueError()
    else:
        wallet.save()
