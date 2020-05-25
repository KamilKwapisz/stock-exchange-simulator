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