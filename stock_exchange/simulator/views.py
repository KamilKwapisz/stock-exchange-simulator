from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, HttpResponse, redirect, reverse
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_variables, sensitive_post_parameters
from djmoney.money import Money

from .forms import AccoutChargeForm, StockBuyForm, StockSellForm, UserForm
from .models import Account, Stock, StockHistory, Wallet, Transaction
from .utils import save_wallets, calculate_fee, sell_stocks


def index(request):
    return render(request, 'index.html', {})


def stock_data(request):
    stock_data = Stock.objects.all()
    return render(request, 'stock_data.html', {'stock_data': stock_data})


class StockDetail(DetailView):
    model = Stock
    template_name = "stock_detail.html"
    context_object_name = "stocks"
    slug_url_kwarg = "name"

    def get_object(self):
        stock = Stock.objects.get(name=self.kwargs['name'])
        return stock

    def get_historical_data(self):
        historical_data = StockHistory.objects.filter(stock=self.object)
        return historical_data
    
    def get_context_data(self, **kwargs):
        context = super(StockDetail, self).get_context_data(**kwargs)
        context['form'] = StockBuyForm()
        context['form'].fields['stock_pk'].initial = self.object.pk

        account = Account.objects.get(owner=self.request.user)
        context['balance'] = account.balance

        context['historical_data'] = self.get_historical_data()
        return context


class StockBuyFormView(FormView):
    form_class = StockBuyForm
    success_url = '/account'
    template_name = 'stock_detail.html'

    def form_valid(self, form):
        user = self.request.user
        account = Account.objects.get(owner=user)

        number = int(form.cleaned_data.get('number'))
        stoploss = form.cleaned_data.get('stoploss', None)
        if stoploss is not None:
            stoploss = Money(stoploss, "PLN")

        stock_pk = int(form.cleaned_data.get('stock_pk'))
        stock = Stock.objects.get(pk=stock_pk)

        amount = number * stock.price
        if amount > account.balance:
            return super().form_invalid(form)
        
        save_wallets(account, stock, number, stoploss)

        amount += calculate_fee(amount)

        transaction = Transaction(
            user=self.request.user,
            stock=stock,
            operation="buy",
            stocks_number=number,
            stock_price=stock.price
        )
        transaction.save()

        account.balance -= amount
        account.save()
        return super().form_valid(form)


class StockSellFormView(FormView):
    form_class = StockSellForm
    success_url = '/account'
    template_name = 'stock_sell.html'

    def get_context_data(self, **kwargs):
        context = super(StockSellFormView, self).get_context_data(**kwargs)
        context['wallet_pk'] = self.kwargs['wallet_pk']
        return context

    def form_valid(self, form):
        user = self.request.user
        account = Account.objects.get(owner=user)

        number = int(form.cleaned_data.get('number'))
        wallet_pk = self.kwargs['wallet_pk']
        wallet = Wallet.objects.get(pk=wallet_pk)
        stock = wallet.stock

        amount = number * stock.price

        try:
            sell_stocks(wallet, number)
        except ValueError:
            return super().form_invalid(form)

        amount -= calculate_fee(amount)

        account.balance += amount
        account.save()

        transaction = Transaction(
            user=self.request.user,
            stock=stock,
            operation="sell",
            stocks_number=number,
            stock_price=stock.price
        )
        transaction.save()

        return super().form_valid(form)


def account_view(request):
    account = Account.objects.get(owner=request.user)
    return render(request, 'account.html', {'account': account})


class RegisterView(View):
    form_class = UserForm
    template_name = 'register.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    @method_decorator(sensitive_variables())
    @method_decorator(sensitive_post_parameters())
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid() and form.cleaned_data['password'] == form.cleaned_data['password_confirm']:
            user = form.save()
            user.set_password(user.password)
            user.save()
            login(self.request, user)

            return redirect(reverse('index'))
        elif form.cleaned_data['password'] != form.cleaned_data['password_confirm']:
            form.add_error('password_confirm', 'Passwords do not match')

        return render(request, self.template_name, {'form': form})


def logout_view(request):
    logout(request)
    return render(request, 'logged_out.html', {})


class ChargeAccountView(LoginRequiredMixin, FormView):
    template_name = 'charge.html'
    form_class = AccoutChargeForm
    success_url = '/account'

    def form_valid(self, form):
        user = self.request.user
        account = Account.objects.get(owner=user)
        amount = float(form.cleaned_data.get('amount'))
        money = Money(amount, 'PLN')
        account.balance += money
        account.save()
        return super().form_valid(form)
