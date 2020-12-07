from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _

from djmoney.money import Money
from djmoney.models.fields import MoneyField



class Account(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = MoneyField(max_digits=14, decimal_places=2, default_currency='PLN')
    wallets = models.ManyToManyField('Wallet')
    transaction_fee = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True, default=getattr(settings, "PERCENTAGE_FEE", 0.0))
    transaction_minimal_fee = MoneyField(max_digits=14,decimal_places=2, default_currency='PLN', default=getattr(settings, "MINIMAL_FEE", 0.0))

    def calculate_fee(self, amount) -> Money:
        fee = amount * (self.transaction_fee / 100)
        if fee < self.transaction_minimal_fee:
            fee = self.transaction_minimal_fee
        else:
            fee = Money(fee, "PLN")
        return fee

    def __str__(self):
        return f"{self.owner} account [{self.balance}]"


class Stock(models.Model):
    TENDENTION = [
       ("up", _('Price going up')),
       ("down", _('Price goin down')),
    ]

    name = models.CharField(max_length=256)
    short_name = models.CharField(max_length=8)
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='PLN')
    timestamp = models.DateTimeField()
    logo_filename = models.CharField(max_length=64, blank=True, null=True)
    logo_path = models.CharField(max_length=64, blank=True, null=True)
    tendention = models.CharField(choices=TENDENTION, max_length=32, default="up")

    def __str__(self):
        return f"{self.name}[{self.short_name}] - {self.price}"


class Transaction(models.Model):
    OPERATIONS = (
       ('buy', _('Kupno')),
       ('sell', _('Sprzedaż')),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    operation = models.CharField(max_length=4, choices=OPERATIONS)
    stocks_number = models.IntegerField()
    stock_price = MoneyField(max_digits=14, decimal_places=2, default_currency='PLN')
    fee = MoneyField(max_digits=14, decimal_places=2, default_currency='PLN', blank=True, null=True)

    @property
    def amount(self):
        return self.stocks_number * self.stock_price

    def __str__(self):
        return f"{self.user.username} -- {self.operation}"


class Wallet(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    number = models.IntegerField(default=1)
    stoploss = MoneyField(max_digits=14, decimal_places=2, null=True, default_currency='PLN')

    @property
    def amount(self):
        return self.number * self.stock.price

    def __str__(self):
        return f"{self.number} akcji {self.stock.name} -> {self.amount}"


class StockHistory(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='PLN')

    class Meta:
        verbose_name_plural = "stock historical data"

    def __str__(self):
        return f"{self.stock.short_name} at {self.price} ({self.timestamp})"
