from django.conf import settings
from django.db import models

from core.models import TimeStampedModel
from menu.models import Menu


class Supplier(models.Model):
    name = models.CharField(max_length=100, unique=True)
    contact_info = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    UNIT_CHOICES = [
        ('g', 'Grams'),
        ('kg', 'Kilograms'),
        ('ml', 'Millilitres'),
        ('l', 'Litres'),
        ('pcs', 'Pieces'),
    ]

    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg')
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reorder_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cost_per_unit = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='ingredients')

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return self.current_stock <= self.reorder_threshold


class RecipeItem(models.Model):
    """Bill of materials: how much of an ingredient one unit of a menu
    item consumes. Lets an order automatically deduct real stock."""

    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='recipe_items')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, related_name='recipe_items')
    quantity_required = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        unique_together = ('menu_item', 'ingredient')

    def __str__(self):
        return f'{self.menu_item.item_name} needs {self.quantity_required}{self.ingredient.unit} {self.ingredient.name}'


class StockMovement(TimeStampedModel):
    REASON_PURCHASE = 'purchase'
    REASON_ORDER_DEDUCTION = 'order_deduction'
    REASON_WASTE = 'waste'
    REASON_ADJUSTMENT = 'adjustment'
    REASON_CHOICES = [
        (REASON_PURCHASE, 'Purchase'),
        (REASON_ORDER_DEDUCTION, 'Order deduction'),
        (REASON_WASTE, 'Waste'),
        (REASON_ADJUSTMENT, 'Manual adjustment'),
    ]

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='stock_movements')
    quantity_delta = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    reference_order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_movements')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='stock_movements')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        sign = '+' if self.quantity_delta >= 0 else ''
        return f'{self.ingredient.name} {sign}{self.quantity_delta}{self.ingredient.unit} ({self.reason})'
