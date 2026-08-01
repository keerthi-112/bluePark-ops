from decimal import Decimal

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.utils import timezone

from analytics import services
from analytics.dateranges import resolve_range
from menu.models import Category, Menu
from orders.models import Order, OrderStatusHistory
from orders.services import add_item_to_cart, advance_order_status, create_order_from_cart, get_active_cart


class DateRangeTests(TestCase):
    def test_defaults_to_7d_when_missing(self):
        request = RequestFactory().get('/api/v1/analytics/summary/')
        start, end, range_key = resolve_range(request)
        self.assertEqual(range_key, '7d')
        self.assertEqual((end.date() - start.date()).days, 6)

    def test_today_is_a_single_day(self):
        request = RequestFactory().get('/api/v1/analytics/summary/?range=today')
        start, end, range_key = resolve_range(request)
        self.assertEqual(range_key, 'today')
        self.assertEqual(start.date(), end.date())

    def test_invalid_custom_dates_fall_back_to_7d(self):
        request = RequestFactory().get('/api/v1/analytics/summary/?range=custom&start=not-a-date&end=also-not-a-date')
        start, end, range_key = resolve_range(request)
        self.assertEqual(range_key, '7d')

    def test_custom_range_with_start_after_end_falls_back_to_7d(self):
        request = RequestFactory().get('/api/v1/analytics/summary/?range=custom&start=2026-01-10&end=2026-01-01')
        start, end, range_key = resolve_range(request)
        self.assertEqual(range_key, '7d')

    def test_valid_custom_range_is_used(self):
        request = RequestFactory().get('/api/v1/analytics/summary/?range=custom&start=2026-01-01&end=2026-01-05')
        start, end, range_key = resolve_range(request)
        self.assertEqual(range_key, 'custom')
        self.assertEqual(start.date().isoformat(), '2026-01-01')
        self.assertEqual(end.date().isoformat(), '2026-01-05')


class AnalyticsSectionTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user('analytics_customer', password='x')
        self.chef = User.objects.create_user('analytics_chef', password='x')
        self.chef.profile.role = 'chef'
        self.chef.profile.save()

        category = Category.objects.create(name='Mains', slug='mains')
        self.item = Menu.objects.create(
            item_name='Test Dish', category=category, description='test',
            price=Decimal('100.00'), is_available=True,
        )
        self.now = timezone.now()
        self.start = self.now - timezone.timedelta(days=1)
        self.end = self.now + timezone.timedelta(days=1)

    def _place_order(self, quantity=1, status=None):
        cart = get_active_cart(self.customer)
        add_item_to_cart(cart, self.item, quantity=quantity)
        order = create_order_from_cart(
            cart, customer=self.customer, order_type=Order.ORDER_TYPE_DELIVERY, payment_method=Order.PAYMENT_METHOD_COD,
        )
        if status:
            advance_order_status(order, status, changed_by=self.chef)
        return order

    def test_revenue_excludes_cancelled_orders(self):
        self._place_order(quantity=2)  # 200.00, stays 'received'
        self._place_order(quantity=1, status=Order.STATUS_CANCELLED)  # 100.00, excluded

        result = services.get_revenue_summary(self.start, self.end)
        self.assertEqual(result['total_revenue'], 200.0)

    def test_orders_summary_cancellation_rate(self):
        self._place_order(quantity=1)
        self._place_order(quantity=1, status=Order.STATUS_CANCELLED)

        result = services.get_orders_summary(self.start, self.end)
        self.assertEqual(result['total_orders'], 2)
        self.assertEqual(result['cancelled_count'], 1)
        self.assertEqual(result['cancellation_rate'], 50.0)

    def test_menu_performance_aggregates_across_orders(self):
        self._place_order(quantity=2)
        self._place_order(quantity=3)

        result = services.get_menu_performance(self.start, self.end)
        row = result['top_by_quantity'][0]
        self.assertEqual(row['item_name'], 'Test Dish')
        self.assertEqual(row['quantity_sold'], 5)
        self.assertEqual(row['revenue'], 500.0)

    def test_kitchen_summary_computes_average_fulfillment_minutes(self):
        order = self._place_order(quantity=1)
        advance_order_status(order, Order.STATUS_PREPARING, changed_by=self.chef)
        advance_order_status(order, Order.STATUS_COMPLETED, changed_by=self.chef)

        placed_at = order.placed_at
        OrderStatusHistory.objects.filter(order=order, to_status=Order.STATUS_PREPARING).update(
            changed_at=placed_at + timezone.timedelta(minutes=5)
        )
        OrderStatusHistory.objects.filter(order=order, to_status=Order.STATUS_COMPLETED).update(
            changed_at=placed_at + timezone.timedelta(minutes=20)
        )

        result = services.get_kitchen_summary(self.start, self.end)
        self.assertEqual(result['avg_minutes_to_preparing'], 5.0)
        self.assertEqual(result['avg_minutes_to_completed'], 20.0)

    def test_staff_summary_hours_worked(self):
        from staff.models import Attendance, Employee

        employee = Employee.objects.create(user=self.chef, position='Chef')
        Attendance.objects.create(
            employee=employee,
            check_in=self.now - timezone.timedelta(hours=3),
            check_out=self.now,
        )

        result = services.get_staff_summary(self.start, self.end)
        self.assertEqual(result['total_hours_worked'], 3.0)
        self.assertEqual(result['hours_by_employee'][0]['employee'], 'analytics_chef')

    def test_inventory_summary_low_stock_and_consumption(self):
        from inventory.models import Ingredient
        from inventory.services import adjust_stock

        ingredient = Ingredient.objects.create(name='Test Ingredient', unit='kg', current_stock=Decimal('1'), reorder_threshold=Decimal('5'))
        adjust_stock(ingredient, Decimal('-2'), reason='order_deduction')

        result = services.get_inventory_summary(self.start, self.end)
        self.assertEqual(result['low_stock_count'], 1)
        self.assertEqual(result['most_consumed'][0]['ingredient_name'], 'Test Ingredient')
        self.assertEqual(result['most_consumed'][0]['quantity_consumed'], 2.0)
