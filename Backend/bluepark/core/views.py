from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from .constants import ROLE_ADMIN, ROLE_MANAGER

MANAGER_ROLES = {ROLE_MANAGER, ROLE_ADMIN}


@login_required
def manager_overview(request):
    role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if role not in MANAGER_ROLES:
        raise PermissionDenied('The overview dashboard is only available to Manager/Admin.')

    from inventory.services import get_low_stock_ingredients
    from orders.models import Order
    from orders.services import get_active_orders
    from staff.models import Attendance

    today = timezone.localdate()

    active_orders_count = get_active_orders().count()
    todays_orders_count = Order.objects.filter(placed_at__date=today).count()
    low_stock_count = get_low_stock_ingredients().count()
    staff_on_shift = Attendance.objects.filter(check_out__isnull=True).count()

    status_rows = Order.objects.filter(placed_at__date=today).values('status').annotate(count=Count('id'))
    status_by_key = {row['status']: row['count'] for row in status_rows}
    status_labels = [label for _, label in Order.STATUS_CHOICES]
    status_data = [status_by_key.get(key, 0) for key, _ in Order.STATUS_CHOICES]

    days = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
    volume_labels = [day.strftime('%a %d') for day in days]
    volume_data = [Order.objects.filter(placed_at__date=day).count() for day in days]

    return render(request, 'manager_overview.html', {
        'active_orders_count': active_orders_count,
        'todays_orders_count': todays_orders_count,
        'low_stock_count': low_stock_count,
        'staff_on_shift': staff_on_shift,
        'chart_data': {
            'status_labels': status_labels,
            'status_data': status_data,
            'volume_labels': volume_labels,
            'volume_data': volume_data,
        },
    })
