"""Bridges the synchronous orders.signals events to the async Channels
layer -- Django signal dispatch is sync, channel_layer.group_send isn't,
so every handler here goes through async_to_sync."""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from orders.models import Order
from orders.serializers import OrderSerializer
from orders.signals import order_placed, order_status_changed

from .consumers import GROUP_NAME

TERMINAL_STATUSES = {Order.STATUS_COMPLETED, Order.STATUS_CANCELLED}


def _broadcast(payload):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(GROUP_NAME, {'type': 'kitchen.update', 'payload': payload})


def handle_order_placed(sender, order, **kwargs):
    _broadcast({'event': 'order_created', 'order': OrderSerializer(order).data})


def handle_order_status_changed(sender, order, old_status, new_status, changed_by, **kwargs):
    if new_status in TERMINAL_STATUSES:
        _broadcast({'event': 'order_removed', 'order_id': order.id})
    else:
        _broadcast({
            'event': 'order_updated',
            'order': OrderSerializer(order).data,
            'old_status': old_status,
            'new_status': new_status,
        })


order_placed.connect(handle_order_placed, dispatch_uid='kitchen_broadcast_order_placed')
order_status_changed.connect(handle_order_status_changed, dispatch_uid='kitchen_broadcast_order_status_changed')
