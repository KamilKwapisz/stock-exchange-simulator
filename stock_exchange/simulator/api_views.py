from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Stock
from . import serializers


class StockViewset(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = serializers.StockSerializer


@api_view(['GET'])
def get_stock_detail(request, pk):
    stock = Stock.objects.get(pk=pk)
    serializer = serializers.StockSerializer(stock)
    return Response(serializer.data)
