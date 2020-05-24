from django.contrib.auth.models import User
from django.db import models
from djmoney.models.fields import MoneyField


class Account(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = MoneyField(max_digits=14, decimal_places=2, default_currency='PLN')
    stocks = models.ManyToManyField('Stock')

    def __str__(self):
        return f"{self.owner} account [{self.balance} PLN]"


class Stock(models.Model):
    name = models.CharField(max_length=256)
    short_name = models.CharField(max_length=8)
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='PLN')
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}[{self.short_name}]"
