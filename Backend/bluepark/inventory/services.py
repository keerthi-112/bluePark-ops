"""Business logic for stock, mirroring orders/services.py's pattern:
one place both the API and any signal handlers call, so there's a
single implementation of "what happens when stock changes."""

from django.db import transaction
from django.db.models import F

from .models import Ingredient, StockMovement


def adjust_stock(ingredient, quantity_delta, reason, created_by=None, reference_order=None):
    ingredient.current_stock += quantity_delta
    ingredient.save(update_fields=['current_stock'])
    return StockMovement.objects.create(
        ingredient=ingredient,
        quantity_delta=quantity_delta,
        reason=reason,
        created_by=created_by,
        reference_order=reference_order,
    )


@transaction.atomic
def deduct_stock_for_order(order):
    """Called via orders.signals.order_placed -- decrements each
    ingredient consumed by the order's items per their RecipeItem BOM.
    Items with no recipe defined yet simply don't move any stock (no
    error) so inventory can be rolled out incrementally per menu item."""

    movements = []
    for order_item in order.items.select_related('menu_item').prefetch_related('menu_item__recipe_items__ingredient'):
        for recipe_item in order_item.menu_item.recipe_items.all():
            quantity_used = recipe_item.quantity_required * order_item.quantity
            movements.append(adjust_stock(
                recipe_item.ingredient,
                quantity_delta=-quantity_used,
                reason=StockMovement.REASON_ORDER_DEDUCTION,
                reference_order=order,
            ))
    return movements


def get_low_stock_ingredients():
    return Ingredient.objects.filter(current_stock__lte=F('reorder_threshold'))
