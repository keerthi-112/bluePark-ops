from orders.signals import order_placed

from .services import deduct_stock_for_order


def handle_order_placed(sender, order, **kwargs):
    deduct_stock_for_order(order)


order_placed.connect(handle_order_placed, dispatch_uid='inventory_deduct_stock_on_order_placed')
