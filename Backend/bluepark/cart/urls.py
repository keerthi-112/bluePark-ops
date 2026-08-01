from django.urls import path
from . import views

urlpatterns = [
    path('cart',views.cart_add, name='cart_add'),
    #path('cart/create/',  views.CreateCartItem.as_view(), name='cart_add'),
    path('cart/update',views.cart_update, name='cart_update'),
]