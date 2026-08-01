from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from menu.models import Category, Menu
from orders.models import Cart, CartItem, Order, OrderStatusHistory
from orders.services import (
    EmptyCartError,
    add_item_to_cart,
    advance_order_status,
    create_order_from_cart,
    get_active_cart,
)


class OrderPipelineTests(TestCase):
    """The cart -> order pipeline is the single most-depended-on path
    across every phase of this project (checkout, kitchen queue,
    inventory deduction, notifications, analytics all sit on top of
    it) -- this is the regression test that most needs to keep
    passing."""

    def setUp(self):
        self.customer = User.objects.create_user('pipeline_customer', password='x')
        category = Category.objects.create(name='Mains', slug='mains')
        self.item = Menu.objects.create(
            item_name='Test Dish', category=category, description='test',
            price=Decimal('150.00'), is_available=True,
        )

    def test_empty_cart_cannot_be_checked_out(self):
        cart = get_active_cart(self.customer)
        with self.assertRaises(EmptyCartError):
            create_order_from_cart(cart, customer=self.customer, order_type=Order.ORDER_TYPE_DELIVERY, payment_method=Order.PAYMENT_METHOD_COD)

    def test_create_order_from_cart_computes_total_and_deactivates_cart(self):
        cart = get_active_cart(self.customer)
        add_item_to_cart(cart, self.item, quantity=3)

        order = create_order_from_cart(
            cart, customer=self.customer, order_type=Order.ORDER_TYPE_DELIVERY,
            payment_method=Order.PAYMENT_METHOD_COD, delivery_address='123 Test St', phone='9999999999',
        )

        self.assertEqual(order.total_amount, Decimal('450.00'))  # 3 x 150.00
        self.assertEqual(order.status, Order.STATUS_RECEIVED)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().unit_price_at_order_time, Decimal('150.00'))

        cart.refresh_from_db()
        self.assertFalse(cart.is_active)

        # A new add-to-cart call gets a fresh cart, not the deactivated one.
        new_cart = get_active_cart(self.customer)
        self.assertNotEqual(new_cart.pk, cart.pk)

    def test_price_change_after_order_does_not_rewrite_history(self):
        cart = get_active_cart(self.customer)
        add_item_to_cart(cart, self.item, quantity=1)
        order = create_order_from_cart(
            cart, customer=self.customer, order_type=Order.ORDER_TYPE_DELIVERY, payment_method=Order.PAYMENT_METHOD_COD,
        )

        self.item.price = Decimal('999.00')
        self.item.save(update_fields=['price'])

        order.refresh_from_db()
        self.assertEqual(order.items.first().unit_price_at_order_time, Decimal('150.00'))
        self.assertEqual(order.total_amount, Decimal('150.00'))

    def test_add_item_to_cart_increments_existing_quantity(self):
        cart = get_active_cart(self.customer)
        add_item_to_cart(cart, self.item, quantity=1)
        add_item_to_cart(cart, self.item, quantity=2)

        self.assertEqual(CartItem.objects.filter(cart=cart, menu_item=self.item).count(), 1)
        self.assertEqual(cart.items.get(menu_item=self.item).quantity, 3)

    def test_advance_order_status_records_history(self):
        cart = get_active_cart(self.customer)
        add_item_to_cart(cart, self.item, quantity=1)
        order = create_order_from_cart(
            cart, customer=self.customer, order_type=Order.ORDER_TYPE_DELIVERY, payment_method=Order.PAYMENT_METHOD_COD,
        )
        chef = User.objects.create_user('pipeline_chef', password='x')
        chef.profile.role = 'chef'
        chef.profile.save()

        advance_order_status(order, Order.STATUS_PREPARING, changed_by=chef)

        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_PREPARING)
        history = list(order.status_history.all())
        self.assertEqual(len(history), 2)  # initial 'received' + this transition
        self.assertEqual(history[-1].from_status, Order.STATUS_RECEIVED)
        self.assertEqual(history[-1].to_status, Order.STATUS_PREPARING)
        self.assertEqual(history[-1].changed_by, chef)
