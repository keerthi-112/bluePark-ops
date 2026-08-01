"""Aggregation functions for the analytics dashboard. Each function
takes a resolved (start, end) datetime pair -- see dateranges.py -- and
returns a plain dict of JSON-ready primitives. Every query here is a
single aggregate/annotate call; nothing loops over a queryset issuing
one query per row (see the module docstring in dateranges.py and the
Phase 3 plan for why that distinction matters)."""

from decimal import Decimal

from django.db.models import Avg, Count, F, Q, Sum
from django.db.models.functions import TruncDate

from orders.models import Order, OrderItem

MENU_PERFORMANCE_LIMIT = 10


def _json_number(value):
    """Casts Decimal aggregates to float (so revenue sums serialize as
    JSON numbers, not DRF's default Decimal-as-string) while leaving
    int aggregates (counts) as ints rather than floats."""
    if isinstance(value, Decimal):
        return float(value)
    return value or 0


def _daily_series(queryset, date_field, value_annotation, value_key):
    """Shared helper: one query producing a value per calendar day in
    the queryset's range, used by both revenue and orders sections so
    the TruncDate-bucketing logic exists in exactly one place."""

    rows = (
        queryset
        .annotate(day=TruncDate(date_field))
        .values('day')
        .annotate(**{value_key: value_annotation})
        .order_by('day')
    )
    return [{'date': row['day'].isoformat(), value_key: _json_number(row[value_key])} for row in rows]


def get_revenue_summary(start, end):
    orders = Order.objects.filter(placed_at__range=(start, end)).exclude(status=Order.STATUS_CANCELLED)

    totals = orders.aggregate(
        total_revenue=Sum('total_amount'),
        average_order_value=Avg('total_amount'),
    )
    daily = _daily_series(orders, 'placed_at', Sum('total_amount'), 'revenue')

    return {
        'total_revenue': float(totals['total_revenue'] or 0),
        'average_order_value': float(totals['average_order_value'] or 0),
        'daily': daily,
    }


def get_orders_summary(start, end):
    orders = Order.objects.filter(placed_at__range=(start, end))

    counts = orders.aggregate(
        total=Count('id'),
        cancelled=Count('id', filter=Q(status=Order.STATUS_CANCELLED)),
    )
    total = counts['total']
    cancelled = counts['cancelled']

    status_rows = orders.values('status').annotate(count=Count('id'))
    status_by_key = {row['status']: row['count'] for row in status_rows}
    status_labels = [label for _, label in Order.STATUS_CHOICES]
    status_data = [status_by_key.get(key, 0) for key, _ in Order.STATUS_CHOICES]

    daily = _daily_series(orders, 'placed_at', Count('id'), 'count')

    return {
        'total_orders': total,
        'cancelled_count': cancelled,
        'cancellation_rate': round((cancelled / total * 100), 1) if total else 0.0,
        'status_labels': status_labels,
        'status_data': status_data,
        'daily': daily,
    }


def get_menu_performance(start, end, limit=MENU_PERFORMANCE_LIMIT):
    """Two grouped-aggregate queries -- each proportional to the number
    of distinct menu items sold, not to the number of orders/items."""

    base = (
        OrderItem.objects
        .filter(order__placed_at__range=(start, end))
        .exclude(order__status=Order.STATUS_CANCELLED)
        .values('menu_item__item_name')
        .annotate(
            quantity_sold=Sum('quantity'),
            revenue=Sum(F('quantity') * F('unit_price_at_order_time')),
        )
    )

    def _rows(queryset):
        return [
            {
                'item_name': row['menu_item__item_name'],
                'quantity_sold': row['quantity_sold'],
                'revenue': _json_number(row['revenue']),
            }
            for row in queryset
        ]

    return {
        'top_by_revenue': _rows(base.order_by('-revenue')[:limit]),
        'top_by_quantity': _rows(base.order_by('-quantity_sold')[:limit]),
    }


def build_summary_payload(start, end, range_key):
    """The one place that assembles the full dashboard payload -- both
    the API view and the page view's initial server-render call this,
    so adding a section here is the only place it needs to be added
    (instead of every caller)."""

    return {
        'range': range_key,
        'start': start.date().isoformat(),
        'end': end.date().isoformat(),
        'revenue': get_revenue_summary(start, end),
        'orders': get_orders_summary(start, end),
        'menu': get_menu_performance(start, end),
    }
