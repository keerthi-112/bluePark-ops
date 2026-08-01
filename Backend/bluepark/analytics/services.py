"""Aggregation functions for the analytics dashboard. Each function
takes a resolved (start, end) datetime pair -- see dateranges.py -- and
returns a plain dict of JSON-ready primitives. Every query here is a
single aggregate/annotate call; nothing loops over a queryset issuing
one query per row (see the module docstring in dateranges.py and the
Phase 3 plan for why that distinction matters)."""

from decimal import Decimal

from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Q, Sum
from django.db.models.functions import TruncDate

from orders.models import Order, OrderItem

MENU_PERFORMANCE_LIMIT = 10
MOST_CONSUMED_LIMIT = 10
STAFF_HOURS_LIMIT = 10


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


def get_inventory_summary(start, end, limit=MOST_CONSUMED_LIMIT):
    from inventory.models import StockMovement
    from inventory.services import get_low_stock_ingredients

    # Snapshot, not range-bound -- "how many ingredients are low right
    # now" doesn't depend on the dashboard's date filter.
    low_stock_count = get_low_stock_ingredients().count()

    movements = StockMovement.objects.filter(created_at__range=(start, end))

    reason_rows = movements.values('reason').annotate(total=Sum('quantity_delta'))
    reason_by_key = {row['reason']: _json_number(row['total']) for row in reason_rows}
    reason_labels = [label for _, label in StockMovement.REASON_CHOICES]
    reason_data = [reason_by_key.get(key, 0) for key, _ in StockMovement.REASON_CHOICES]

    consumed_rows = (
        movements
        .filter(reason=StockMovement.REASON_ORDER_DEDUCTION)
        .values('ingredient__name', 'ingredient__unit')
        .annotate(consumed=Sum('quantity_delta'))
        .order_by('consumed')  # most negative first = most consumed
    )[:limit]
    most_consumed = [
        {
            'ingredient_name': row['ingredient__name'],
            'unit': row['ingredient__unit'],
            'quantity_consumed': abs(_json_number(row['consumed'])),
        }
        for row in consumed_rows
    ]

    return {
        'low_stock_count': low_stock_count,
        'reason_labels': reason_labels,
        'reason_data': reason_data,
        'most_consumed': most_consumed,
    }


def get_staff_summary(start, end, limit=STAFF_HOURS_LIMIT):
    from staff.models import Attendance, Shift

    total_shifts = Shift.objects.filter(start_time__range=(start, end)).count()
    on_shift_now = Attendance.objects.filter(check_out__isnull=True).count()  # snapshot

    worked = Attendance.objects.filter(
        check_in__range=(start, end),
        check_out__isnull=False,
    )
    duration_expr = ExpressionWrapper(F('check_out') - F('check_in'), output_field=DurationField())

    total_duration = worked.aggregate(total=Sum(duration_expr))['total']
    total_hours = round(total_duration.total_seconds() / 3600, 1) if total_duration else 0.0

    hours_rows = (
        worked
        .annotate(duration=duration_expr)
        .values('employee__user__username')
        .annotate(total_duration=Sum('duration'))
        .order_by('-total_duration')
    )[:limit]
    hours_by_employee = [
        {
            'employee': row['employee__user__username'],
            'hours': round(row['total_duration'].total_seconds() / 3600, 1) if row['total_duration'] else 0.0,
        }
        for row in hours_rows
    ]

    return {
        'total_shifts': total_shifts,
        'on_shift_now': on_shift_now,
        'total_hours_worked': total_hours,
        'hours_by_employee': hours_by_employee,
    }


def get_kitchen_summary(start, end):
    """Average time from an order being placed to it reaching
    preparing/ready/completed. The tricky part: two bulk queries total
    (order id+placed_at, then their status-history rows), never one
    query per order -- durations are then computed with plain dict
    lookups over the already-fetched (small) result sets, which isn't
    N+1: N+1 means issuing a *new query* per row, not doing arithmetic
    in Python after a single fetch."""

    from orders.models import OrderStatusHistory

    orders = Order.objects.filter(placed_at__range=(start, end))

    counts = orders.aggregate(
        total=Count('id'),
        cancelled=Count('id', filter=Q(status=Order.STATUS_CANCELLED)),
    )

    placed_at_by_order = dict(orders.values_list('id', 'placed_at'))
    order_ids = list(placed_at_by_order.keys())

    tracked_statuses = (Order.STATUS_PREPARING, Order.STATUS_READY, Order.STATUS_COMPLETED)
    history_rows = OrderStatusHistory.objects.filter(
        order_id__in=order_ids,
        to_status__in=tracked_statuses,
    ).values_list('order_id', 'to_status', 'changed_at')

    first_reached = {}
    for order_id, to_status, changed_at in history_rows:
        key = (order_id, to_status)
        if key not in first_reached or changed_at < first_reached[key]:
            first_reached[key] = changed_at

    def average_minutes(status):
        durations = [
            (first_reached[(order_id, status)] - placed_at_by_order[order_id]).total_seconds() / 60
            for order_id in order_ids
            if (order_id, status) in first_reached
        ]
        return round(sum(durations) / len(durations), 1) if durations else 0.0

    total = counts['total']
    cancelled = counts['cancelled']

    return {
        'avg_minutes_to_preparing': average_minutes(Order.STATUS_PREPARING),
        'avg_minutes_to_ready': average_minutes(Order.STATUS_READY),
        'avg_minutes_to_completed': average_minutes(Order.STATUS_COMPLETED),
        'cancellation_rate': round((cancelled / total * 100), 1) if total else 0.0,
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
        'inventory': get_inventory_summary(start, end),
        'staff': get_staff_summary(start, end),
        'kitchen': get_kitchen_summary(start, end),
    }
