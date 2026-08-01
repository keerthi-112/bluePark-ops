from django.urls import path

from . import api

urlpatterns = [
    path('ingredients/', api.IngredientListCreateView.as_view(), name='api_ingredients'),
    path('stock-movements/', api.StockMovementListCreateView.as_view(), name='api_stock_movements'),
    path('low-stock/', api.LowStockView.as_view(), name='api_low_stock'),
]
