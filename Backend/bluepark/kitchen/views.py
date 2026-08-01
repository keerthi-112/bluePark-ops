from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from core.constants import ROLE_ADMIN, ROLE_CHEF, ROLE_MANAGER
from orders.models import Order
from orders.services import advance_order_status, get_active_orders

KITCHEN_ROLES = {ROLE_CHEF, ROLE_MANAGER, ROLE_ADMIN}

NEXT_STATUS = {
    Order.STATUS_RECEIVED: Order.STATUS_PREPARING,
    Order.STATUS_PREPARING: Order.STATUS_READY,
    Order.STATUS_READY: Order.STATUS_COMPLETED,
}


@login_required
def queue(request):
    role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if role not in KITCHEN_ROLES:
        raise PermissionDenied('The kitchen queue is only available to kitchen staff.')

    if request.method == 'POST':
        order = get_object_or_404(Order, pk=request.POST.get('order_id'))
        new_status = request.POST.get('new_status')
        if new_status in dict(Order.STATUS_CHOICES):
            advance_order_status(order, new_status, changed_by=request.user)
            messages.info(request, f'Order #{order.id} marked {order.get_status_display()}.')
        return redirect('kitchen_queue')

    columns = {
        Order.STATUS_RECEIVED: {'label': 'Received', 'next_status': NEXT_STATUS[Order.STATUS_RECEIVED], 'orders': []},
        Order.STATUS_PREPARING: {'label': 'Preparing', 'next_status': NEXT_STATUS[Order.STATUS_PREPARING], 'orders': []},
        Order.STATUS_READY: {'label': 'Ready', 'next_status': NEXT_STATUS[Order.STATUS_READY], 'orders': []},
    }
    for order in get_active_orders():
        columns[order.status]['orders'].append(order)

    return render(request, 'kitchen_queue.html', {'columns': columns.values()})
