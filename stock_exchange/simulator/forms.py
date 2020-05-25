from django.contrib.auth.forms import User
from django import forms
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MaxMoneyValidator, MinMoneyValidator


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class AccoutCharge(forms.Form):
    amount = forms.MoneyField(
        decimal_places=2,
        validators=[
            MinMoneyValidator(10),
            MaxMoneyValidator(1000000),
        ]
    )
