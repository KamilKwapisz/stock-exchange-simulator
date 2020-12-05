from django.contrib.auth.forms import User
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from simulator.models import Account


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class AccoutChargeForm(forms.Form):
    amount = forms.DecimalField(
        decimal_places=2, 
        validators=(
            MinValueValidator(10.0),
            MaxValueValidator(1000000.0)
        )
    )


class StockBuyForm(forms.Form):
    number = forms.IntegerField(min_value=1, max_value=1000000)
    stock_pk = forms.IntegerField(widget=forms.HiddenInput())
    stoploss = forms.DecimalField(
        decimal_places=2, 
        validators=(
            MinValueValidator(0.0),
            MaxValueValidator(1000000.0)
        ),
        required=False
    )


class StockSellForm(forms.Form):
    number = forms.IntegerField(min_value=1, max_value=1000000)


class StockSettingsForm(forms.ModelForm):
    transaction_fee = forms.DecimalField(decimal_places=2, required=False)
    transaction_minimal_fee = forms.DecimalField(decimal_places=2, required=False)

    class Meta:
        model = Account
        fields = [
            'transaction_fee',
            'transaction_minimal_fee',
        ]
