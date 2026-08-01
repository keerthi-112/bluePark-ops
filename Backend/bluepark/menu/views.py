from django.shortcuts import render
from accounts import views
from survey import views
from .models import Menu

from orders.serializers import CartSerializer
from orders.services import get_active_cart

# Create your views here.
def home(request):
    menu_items = Menu.objects.filter(is_available=True).select_related('category')
    cart_data = None
    if request.user.is_authenticated:
        cart_data = CartSerializer(get_active_cart(request.user)).data
    return render(request,'homepage.html',{'menu_items':menu_items, 'cart_data': cart_data})

