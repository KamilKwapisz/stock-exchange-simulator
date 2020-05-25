from django.contrib.auth.forms import User
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator


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
