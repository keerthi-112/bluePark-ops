from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from core.constants import ROLE_ADMIN, ROLE_MANAGER
from .models import Ingredient

MANAGER_ROLES = {ROLE_MANAGER, ROLE_ADMIN}


@login_required
def dashboard(request):
    role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if role not in MANAGER_ROLES:
        raise PermissionDenied('Inventory is only available to Manager/Admin.')

    ingredients = Ingredient.objects.select_related('supplier').order_by('name')
    low_stock_count = sum(1 for i in ingredients if i.is_low_stock)

    return render(request, 'inventory_dashboard.html', {
        'ingredients': ingredients,
        'low_stock_count': low_stock_count,
        'total_count': ingredients.count(),
    })
