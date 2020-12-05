from django.urls import path
from django.contrib.auth.views import LoginView
from django.views.decorators.http import require_POST

from . import views

app_name = 'simulator'

urlpatterns = [
    path('', views.index, name='index'),
    path('login', LoginView.as_view(template_name='login.html'), name='login'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('logout', views.logout_view, name='logout'),

    path('stock', views.stock_data, name='stock_data'),
    path('stock/<slug:name>', views.StockDetail.as_view(), name='stock_detail'),
    path('buy-stock', require_POST(views.StockBuyFormView.as_view()), name='buy_stock'),
    path('sell-stock/<int:wallet_pk>', views.StockSellFormView.as_view(), name='sell_stock'),
    path('account', views.account_view, name='account'),
    path('transaction-history', views.transaction_history_view, name='transaction-history'),
    path('charge-account', views.ChargeAccountView.as_view(), name='charge_account'),
    path('download/stock', views.download_stock_data, name='download_stock_data'),

]