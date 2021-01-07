from django.contrib.auth.models import User
from djmoney.money import Money
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Account, Stock, Transaction, Wallet
from . import serializers
from .utils import save_wallets, sell_stocks


class StockViewset(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = serializers.StockSerializer


@api_view(['GET'])
def get_stock_detail(request, pk):
    stock = Stock.objects.get(pk=pk)
    serializer = serializers.StockSerializer(stock)
    return Response(serializer.data)


@api_view(['GET'])
def get_account_details(request):
    pk = 1  # TODO
    account = Account.objects.get(pk=1)
    serializer = serializers.AccountSerializer(account)
    return Response(serializer.data)


@api_view(['POST'])
def set_fee_values(request):
    pk = 1  # TODO
    account = Account.objects.get(pk=1)
    transaction_fee = request.POST.get('transaction_fee')
    transaction_minimal_fee = request.POST.get('transaction_minimal_fee')
    if transaction_fee is not None:
        try:
            transaction_fee = float(transaction_fee)
        except ValueError:
            return Response({
                    'status': "Failure",
                    'message': "Niepoprawna wartość prowizji."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if transaction_fee < 0:
            return Response({
                'status': "Failure",
                'message': "Wartości prowizji muszą być nieujemne."
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        account.transaction_fee = transaction_fee
        
    if transaction_minimal_fee is not None:
        try:
            transaction_minimal_fee = float(transaction_minimal_fee)
        except ValueError:
            return Response({
                    'status': "Failure",
                    'message': "Niepoprawna wartość minimalnej prowizji."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if transaction_minimal_fee < 0:
            return Response({
                'status': "Failure",
                'message': "Wartości prowizji muszą być nieujemne."
            },
            status=status.HTTP_400_BAD_REQUEST
            )
        account.transaction_minimal_fee = transaction_minimal_fee
    
    account.save()
    return Response({
            'status': "Success",
            'message': f"Zaktualizowano wartości prowizji. Aktualne wartości prowizji: {account.transaction_fee}({account.transaction_minimal_fee})"
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
def charge_account(request):
    pk = 1  # TODO
    account = Account.objects.get(pk=1)
    amount = request.POST.get('amount', 0)
    try:
        amount = float(amount)
    except ValueError:
        return Response({
                'status': "Failure",
                'message': "Błędna wartość kwoty doładowania konta."
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    if amount < 0:
        return Response({
                'status': "Failure",
                'message': "Wartość doładowania nie może być ujemna."
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    money = Money(amount, 'PLN')
    account.balance += money
    account.save()
    return Response({
            'status': "Success",
            'message': f"Zaktualizowano saldo konta. Aktualne saldo: {account.balance}"
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
def get_transaction_history(request):
    pk = 1
    user = User.objects.get(pk=pk)
    transactions = Transaction.objects.filter(
        user=user
    ).order_by('-timestamp')
    serializer = serializers.TransactionSerializer(transactions, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def get_wallets(request):
    pk = 1
    account = Account.objects.get(pk=pk)
    serializer = serializers.WalletSerializer(
        account.wallets.all(),
        many=True
    )
    return Response(serializer.data)


@api_view(['POST'])
def buy_stock(request, stock_pk):
    try:
        stock_pk = int(stock_pk)
    except ValueError:
        # użytkownik próbuje użyć symbolu giełdowego
        stock_pk = stock_pk.upper()
    stocks_number = request.POST.get('number')
    stoploss = request.POST.get('stoploss')
    if stocks_number is not None:
        try:
            stocks_number = int(stocks_number)
        except ValueError:
            return Response({
                    'status': "Failure",
                    'message': "Niepoprawna liczba akcji."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if stocks_number <= 0:
            return Response({
                    'status': "Failure",
                    'message': "Liczba akcji musi być liczbą dodatnią."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    if stoploss is not None:
        try:
            stoploss = float(stoploss)
        except ValueError:
            return Response({
                    'status': "Failure",
                    'message': "Niepoprawna wartość stoploss."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    pk = 1
    account = Account.objects.get(pk=pk)
    if isinstance(stock_pk, int):
        stock = Stock.objects.get(pk=stock_pk)
    else:
        try:
            stock = Stock.objects.get(short_name=stock_pk)
        except Stock.DoesNotExist:
            return Response({
                    'status': "Failure",
                    'message': f"Brak firmy o symbolu giełdowym {stock_pk}. Użyj poprawnego symbolu giełdowego lub ID"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    amount = stocks_number * stock.price
    if amount > account.balance:
        return Response({
                'status': "Failure",
                'message': "Brak wystarczających środków na koncie."
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    save_wallets(account, stock, stocks_number, stoploss)
    fee = account.calculate_fee(amount)
    amount += fee
    transaction = Transaction(
        user=account.owner,
        stock=stock,
        operation="buy",
        stocks_number=stocks_number,
        stock_price=stock.price,
        fee=fee
    )
    transaction.save()

    account.balance -= amount
    account.save()
    return Response({
            'status': "Success",
            'message': f"Pomyślnie zakupiono {stocks_number} akcji/e firmy {stock.name}. Koszt: {amount}"
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
def sell_stock(request, wallet_pk):
    stocks_number = request.POST.get('number')
    if stocks_number is not None:
        try:
            stocks_number = int(stocks_number)
        except ValueError:
            return Response({
                    'status': "Failure",
                    'message': "Niepoprawna liczba akcji."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if stocks_number <= 0:
            return Response({
                    'status': "Failure",
                    'message': "Liczba akcji musi być liczbą dodatnią."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    try:
        wallet = Wallet.objects.get(pk=wallet_pk)
    except Wallet.DoesNotExist:
        return Response({
                    'status': "Failure",
                    'message': "Akcje nie znajdują się w portfelu."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    stock = wallet.stock
    amount = stocks_number * stock.price
    try:
        sell_stocks(wallet, stocks_number)
    except ValueError:
        return Response({
                'status': "Failure",
                'message': f"Nie możesz sprzedać więcej akcji niż posiadasz w portfelu inwestycyjnym."
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    pk = 1
    user = User.objects.get(pk=pk)
    account = Account.objects.get(owner=user)
    fee = account.calculate_fee(amount)
    amount -= fee

    account.balance += amount
    account.save()

    transaction = Transaction(
        user=user,
        stock=stock,
        operation="sell",
        stocks_number=stocks_number,
        stock_price=stock.price,
        fee=fee
    )
    transaction.save()
    return Response({
            'status': "Success",
            'message': f"Pomyślnie sprzedano {stocks_number} akcji/e firmy {stock.name}. Przychód ze sprzedaży: {abs(amount)}"
        },
        status=status.HTTP_201_CREATED
    )