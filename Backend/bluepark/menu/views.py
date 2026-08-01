from django.db.models import Prefetch
from django.shortcuts import render
from accounts import views
from survey import views
from .models import Category, Menu

from orders.serializers import CartSerializer
from orders.services import get_active_cart

# Create your views here.
def home(request):
    categories = Category.objects.prefetch_related(
        Prefetch('menu_items', queryset=Menu.objects.filter(is_available=True))
    ).order_by('display_order', 'name')
    # Iterating here materializes the (prefetched) queryset once; the
    # template re-iterating the same `categories` object below reuses
    # that cache rather than re-querying.
    has_menu_items = any(category.menu_items.all() for category in categories)
    cart_data = None
    if request.user.is_authenticated:
        cart_data = CartSerializer(get_active_cart(request.user)).data
    return render(request, 'homepage.html', {'categories': categories, 'has_menu_items': has_menu_items, 'cart_data': cart_data})

