from django.contrib import admin

from .models import Account, Stock, Transaction, Wallet, StockHistory, News

admin.site.register(Account)
admin.site.register(Stock)
admin.site.register(Transaction)
admin.site.register(Wallet)
admin.site.register(StockHistory)
admin.site.register(News)
