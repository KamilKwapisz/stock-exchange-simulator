from django.urls import path
from django.contrib.auth.views import LoginView

from . import views

app_name = 'simulator'

urlpatterns = [
    path('', views.index, name='index'),
    path('login', LoginView.as_view(template_name='login.html'), name='login'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('logout', views.logout_view, name='logout'),

    path('stock', views.stock_data, name='stock_data'),
    path('stock/<int:pk>', views.StockDetail.as_view(), name='stock_detail'),
    path('account', views.account_view, name='account'),
]