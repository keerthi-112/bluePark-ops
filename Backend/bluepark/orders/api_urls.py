from django.urls import path

from . import api

urlpatterns = [
    path('cart/', api.CartView.as_view(), name='api_cart'),
    path('cart/items/', api.CartItemListView.as_view(), name='api_cart_items'),
    path('cart/items/<int:item_id>/', api.CartItemDetailView.as_view(), name='api_cart_item_detail'),
    path('', api.OrderListCreateView.as_view(), name='api_order_list_create'),
    path('<int:pk>/', api.OrderDetailView.as_view(), name='api_order_detail'),
    path('<int:pk>/status/', api.OrderStatusUpdateView.as_view(), name='api_order_status'),
]
