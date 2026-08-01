from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from core.constants import ROLE_ADMIN, ROLE_CHEF, ROLE_MANAGER
from orders.models import Order
from orders.serializers import OrderSerializer
from orders.services import get_active_orders

KITCHEN_ROLES = {ROLE_CHEF, ROLE_MANAGER, ROLE_ADMIN}

NEXT_STATUS = {
    Order.STATUS_RECEIVED: Order.STATUS_PREPARING,
    Order.STATUS_PREPARING: Order.STATUS_READY,
    Order.STATUS_READY: Order.STATUS_COMPLETED,
}

COLUMN_ORDER = [Order.STATUS_RECEIVED, Order.STATUS_PREPARING, Order.STATUS_READY]
COLUMN_LABELS = {Order.STATUS_RECEIVED: 'Received', Order.STATUS_PREPARING: 'Preparing', Order.STATUS_READY: 'Ready'}


@login_required
def queue(request):
    role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if role not in KITCHEN_ROLES:
        raise PermissionDenied('The kitchen queue is only available to kitchen staff.')

    orders_by_status = {status: [] for status in COLUMN_ORDER}
    for order in get_active_orders():
        orders_by_status[order.status].append(order)

    initial_data = {
        'columns': [
            {
                'status': status,
                'label': COLUMN_LABELS[status],
                'next_status': NEXT_STATUS[status],
                'orders': OrderSerializer(orders_by_status[status], many=True).data,
            }
            for status in COLUMN_ORDER
        ],
    }

    return render(request, 'kitchen_queue.html', {'initial_data': initial_data})
