"""Business logic for the cart/order pipeline, shared by the DRF API
(orders/api.py) and the server-rendered checkout page (orders/views.py)
so the two never diverge on how a cart becomes an order."""

from django.db import transaction

from .models import Cart, CartItem, Order, OrderItem, OrderStatusHistory


def get_active_cart(user):
    return Cart.get_active_for_user(user)


def add_item_to_cart(cart, menu_item, quantity=1, note=''):
    item, created = CartItem.objects.get_or_create(
        cart=cart, menu_item=menu_item, defaults={'quantity': quantity, 'note': note}
    )
    if not created:
        item.quantity += quantity
        if note:
            item.note = note
        item.save(update_fields=['quantity', 'note'])
    return item


def remove_item_from_cart(cart, cart_item_id):
    CartItem.objects.filter(cart=cart, pk=cart_item_id).delete()


class EmptyCartError(Exception):
    pass


@transaction.atomic
def create_order_from_cart(cart, customer, order_type, payment_method, delivery_address='', phone=''):
    items = list(cart.items.select_related('menu_item'))
    if not items:
        raise EmptyCartError('Cannot place an order from an empty cart.')

    total = sum((item.subtotal for item in items))
    order = Order.objects.create(
        customer=customer,
        order_type=order_type,
        payment_method=payment_method,
        delivery_address=delivery_address,
        phone=phone,
        total_amount=total,
    )
    OrderItem.objects.bulk_create([
        OrderItem(
            order=order,
            menu_item=item.menu_item,
            quantity=item.quantity,
            unit_price_at_order_time=item.menu_item.price,
            note=item.note,
        )
        for item in items
    ])
    OrderStatusHistory.objects.create(
        order=order, from_status='', to_status=Order.STATUS_RECEIVED, changed_by=customer,
    )

    cart.is_active = False
    cart.save(update_fields=['is_active'])

    return order


def advance_order_status(order, new_status, changed_by):
    old_status = order.status
    order.status = new_status
    order.save(update_fields=['status'])
    OrderStatusHistory.objects.create(
        order=order, from_status=old_status, to_status=new_status, changed_by=changed_by,
    )
    return order
