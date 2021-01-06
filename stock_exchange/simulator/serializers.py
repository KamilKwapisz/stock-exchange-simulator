from rest_framework import serializers
from . import models


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Account
        fields = ('id', 'balance', 'transaction_fee', 'transaction_minimal_fee')


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