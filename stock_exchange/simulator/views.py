import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.shortcuts import render, HttpResponse, redirect, reverse
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_variables, sensitive_post_parameters
from djmoney.money import Money

from .forms import AccoutChargeForm, StockBuyForm, StockSellForm, UserForm, StockSettingsForm
from .models import Account, Stock, StockHistory, Wallet, Transaction
from .utils import save_wallets, sell_stocks


def index(request):
    context = {}

    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-timestamp')

    up_tendention_stocks = Stock.objects.filter(tendention="up").order_by('-price')[:6]

    account = Account.objects.get(owner=request.user)

    stocks_number = 0
    stocks_value = 0.0
    for wallet in account.wallets.all():
        stocks_number += wallet.number
        stocks_value += wallet.amount

    context['transactions'] = transactions[:5]
    context['transactions_count'] = transactions[:5].count()
    context['up_tendention_stocks'] = up_tendention_stocks
    context['balance'] = account.balance
    context['transaction_fee'] = account.transaction_fee
    context['transaction_minimal_fee'] = account.transaction_minimal_fee
    context['stocks_number'] = stocks_number
    context['stocks_value'] = stocks_value
    return render(request, 'index.html', context)


def stock_data(request):
    stock_data = Stock.objects.all().order_by('name')
    account = Account.objects.get(owner=request.user)
    context = {
        'stock_data': stock_data,
        'balance': account.balance
    }
    return render(request, 'stock_data.html', context)


class StockDetail(DetailView):
    model = Stock
    template_name = "stock_detail.html"
    context_object_name = "stocks"
    slug_url_kwarg = "name"

    def get_object(self):
        stock = Stock.objects.get(name=self.kwargs['name'])
        return stock

    def __get_historical_data(self):
        historical_data = StockHistory.objects.filter(stock=self.object)
        return historical_data
    
    def get_context_data(self, **kwargs):
        context = super(StockDetail, self).get_context_data(**kwargs)
        context['form'] = StockBuyForm()
        context['form'].fields['stock_pk'].initial = self.object.pk

        account = Account.objects.get(owner=self.request.user)
        context['balance'] = account.balance

        try:
            wallet = account.wallets.get(stock=self.object.pk)
        except Wallet.DoesNotExist:
            context['stocks_in_wallet'] = 0
            context['stocks_value'] = 0
        else:
            context['stocks_in_wallet'] = wallet.number
            context['stocks_value'] = wallet.amount

        context['historical_data'] = self.__get_historical_data()
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
            messages.add_message(
                self.request,
                messages.WARNING, 
                "Brak wystarczających środków na koncie."
            )
            return redirect(reverse('simulator:stock_detail', kwargs={'name': stock.name}))
        
        save_wallets(account, stock, number, stoploss)

        fee = account.calculate_fee(amount)
        amount += fee

        transaction = Transaction(
            user=self.request.user,
            stock=stock,
            operation="buy",
            stocks_number=number,
            stock_price=stock.price,
            fee=fee
        )
        transaction.save()

        account.balance -= amount
        account.save()
        messages.add_message(
            self.request,
            messages.SUCCESS, 
            f"Pomyślnie zakupiono {number} akcji/e firmy {stock.name}. Koszt: {amount}"
        )
        return super().form_valid(form)


class StockSellFormView(FormView):
    form_class = StockSellForm
    success_url = '/account'
    template_name = 'stock_sell.html'

    def get_context_data(self, **kwargs):
        context = super(StockSellFormView, self).get_context_data(**kwargs)
        wallet_pk = self.kwargs['wallet_pk']
        wallet = Wallet.objects.get(pk=wallet_pk)
        context['wallet_pk'] = wallet_pk
        context['stock_name'] = wallet.stock.name
        context['stocks_number'] = wallet.number
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
            messages.add_message(
                self.request,
                messages.WARNING, 
                f"Nie możesz sprzedać więcej akcji niż posiadasz w portfelu inwestycyjnym."
            )
            return redirect(reverse('simulator:account'))

        fee = account.calculate_fee(amount)
        amount -= fee

        account.balance += amount
        account.save()

        transaction = Transaction(
            user=self.request.user,
            stock=stock,
            operation="sell",
            stocks_number=number,
            stock_price=stock.price,
            fee=fee
        )
        transaction.save()

        messages.add_message(
            self.request,
            messages.SUCCESS, 
            f"Pomyślnie sprzedano {number} akcji/e firmy {stock.name}. Przychód ze sprzedaży: {amount}"
        )

        return super().form_valid(form)


def account_view(request):
    account = Account.objects.get(owner=request.user)
    stocks_number = 0
    stocks_value = 0.0
    for wallet in account.wallets.all():
        stocks_number += wallet.number
        stocks_value += wallet.amount
    context = {
        'account': account,
        'stocks_number': stocks_number,
        'stocks_value': stocks_value,
    }
    return render(request, 'account.html', context)


def transaction_history_view(request):
    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-timestamp')
    
    context = {
        'transactions': transactions
    }
    return render(request, 'transaction_history.html', context)


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

            return redirect(reverse('simulator:index'))
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


def download_stock_data(request):
    stock_data_filename = "stock_data.csv"
    file_path = os.path.join(settings.MEDIA_ROOT, stock_data_filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as csv_file:
            response = HttpResponse(csv_file.read(), content_type="application/csv")
            response['Content-Disposition'] = f"attachment;filename={stock_data_filename}"
            return response
    else:
        raise Http404


class StockSettingsFormView(FormView):
    form_class = StockSettingsForm
    success_url = '/account'
    template_name = 'settings.html'

    def get_context_data(self, **kwargs):
        # TODO REFACTOR
        context = super(StockSettingsFormView, self).get_context_data(**kwargs)
        account = Account.objects.get(owner=self.request.user)
        context['transaction_fee'] = str(account.transaction_fee).replace(',', '.')
        context['transaction_minimal_fee'] = str(account.transaction_minimal_fee.amount).replace(',', '.')
        return context

    def form_valid(self, form):
        account = Account.objects.get(owner=self.request.user)

        transaction_fee = form.cleaned_data.get('transaction_fee')
        transaction_minimal_fee = form.cleaned_data.get('transaction_minimal_fee')

        account.transaction_fee = transaction_fee
        account.transaction_minimal_fee = transaction_minimal_fee
        account.save()
        messages.add_message(
            self.request,
            messages.SUCCESS, 
            "Pomyślnie zaktualizowano dane."
        )
        return super().form_valid(form)
