from django.contrib import admin

from .models import Account, Stock, Transaction

admin.site.register(Account)
admin.site.register(Stock)
admin.site.register(Transaction)
