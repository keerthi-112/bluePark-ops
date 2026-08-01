from decimal import Decimal

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel
from menu.models import Menu


class Cart(TimeStampedModel):
    """A user's active shopping cart. `is_active=False` once it's been
    turned into an Order -- a user then gets a fresh Cart on their next add."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user'], condition=models.Q(is_active=True), name='one_active_cart_per_user'),
        ]

    def __str__(self):
        return f'Cart #{self.pk} ({self.user.username})'

    @property
    def total(self):
        return sum((item.subtotal for item in self.items.all()), Decimal('0.00'))

    @classmethod
    def get_active_for_user(cls, user):
        cart, _ = cls.objects.get_or_create(user=user, is_active=True)
        return cart


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveSmallIntegerField(default=1)
    note = models.CharField(max_length=250, blank=True)

    class Meta:
        unique_together = ('cart', 'menu_item')

    def __str__(self):
        return f'{self.quantity} x {self.menu_item.item_name}'

    @property
    def subtotal(self):
        return self.menu_item.price * self.quantity


class Order(TimeStampedModel):
    STATUS_RECEIVED = 'received'
    STATUS_PREPARING = 'preparing'
    STATUS_READY = 'ready'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_RECEIVED, 'Received'),
        (STATUS_PREPARING, 'Preparing'),
        (STATUS_READY, 'Ready'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    ORDER_TYPE_DELIVERY = 'delivery'
    ORDER_TYPE_TAKEAWAY = 'takeaway'
    ORDER_TYPE_DINE_IN = 'dine_in'
    ORDER_TYPE_CHOICES = [
        (ORDER_TYPE_DELIVERY, 'Delivery'),
        (ORDER_TYPE_TAKEAWAY, 'Takeaway'),
        (ORDER_TYPE_DINE_IN, 'Dine-in'),
    ]

    PAYMENT_PENDING = 'pending'
    PAYMENT_PAID = 'paid'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, 'Pending'),
        (PAYMENT_PAID, 'Paid'),
    ]

    PAYMENT_METHOD_COD = 'cod'
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_COD, 'Cash on Delivery'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_RECEIVED)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default=ORDER_TYPE_DELIVERY)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_PENDING)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default=PAYMENT_METHOD_COD)
    delivery_address = models.CharField(max_length=350, blank=True)
    phone = models.CharField(max_length=12, blank=True)
    placed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['placed_at']

    def __str__(self):
        return f'Order #{self.pk} ({self.get_status_display()})'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(Menu, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveSmallIntegerField()
    unit_price_at_order_time = models.DecimalField(max_digits=8, decimal_places=2)
    note = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return f'{self.quantity} x {self.menu_item.item_name} (Order #{self.order_id})'

    @property
    def subtotal(self):
        return self.unit_price_at_order_time * self.quantity


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='order_status_changes')
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['changed_at']
        verbose_name_plural = 'order status histories'

    def __str__(self):
        return f'Order #{self.order_id}: {self.from_status} -> {self.to_status}'
