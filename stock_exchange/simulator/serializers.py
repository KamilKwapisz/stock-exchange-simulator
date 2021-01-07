from rest_framework import serializers
from . import models


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Account
        fields = ('balance', 'transaction_fee', 'transaction_minimal_fee')


class StockSerializer(serializers.ModelSerializer):
    buying_url = serializers.CharField(source='get_buy_url')

    class Meta:
        model = models.Stock
        fields = (
            'id',
            'short_name',
            'full_name',
            'price',
            'tendention',
            'buying_url'
        )


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Transaction
        fields = (
            'timestamp',
            'operation',
            'stocks_number',
            'stock_price',
            'amount'
        )


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Wallet
        fields = (
            'ticker_symbol',
            'number',
            'stoploss',
            'amount',
            'sell_link'
        )
