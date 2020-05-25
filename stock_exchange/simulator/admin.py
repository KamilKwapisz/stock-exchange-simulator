from django.contrib import admin

from .models import Account, Stock, Transaction, Wallet

admin.site.register(Account)
admin.site.register(Stock)
admin.site.register(Transaction)
admin.site.register(Wallet)
