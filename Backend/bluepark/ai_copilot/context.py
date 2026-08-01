"""Gathers the restaurant data the copilot answers questions from.
Reuses analytics.services' six section functions directly -- zero
duplicated aggregation logic -- and adds the one thing analytics
doesn't cover yet: customer feedback."""

from django.db.models import Avg, Count

FEEDBACK_RECENT_LIMIT = 5


def get_feedback_summary(limit=FEEDBACK_RECENT_LIMIT):
    """Survey_feedback (Phase 1) has no timestamp field, so this is an
    all-time snapshot, not range-bound -- same reasoning as inventory's
    low_stock_count and staff's on_shift_now. Ordered by -id as the
    best available proxy for "most recent" given that limitation."""

    from survey.models import Survey_feedback

    feedback = Survey_feedback.objects.all()
    stats = feedback.aggregate(average_rating=Avg('rating'), total_count=Count('id'))
    recent = list(feedback.order_by('-id').values('name', 'rating', 'feed')[:limit])

    return {
        'average_rating': round(stats['average_rating'], 2) if stats['average_rating'] is not None else None,
        'total_feedback_count': stats['total_count'],
        'recent_feedback': recent,
    }


def build_operations_context(start, end):
    from analytics.services import (
        get_inventory_summary,
        get_kitchen_summary,
        get_menu_performance,
        get_orders_summary,
        get_revenue_summary,
        get_staff_summary,
    )

    return {
        'date_range': {'start': start.date().isoformat(), 'end': end.date().isoformat()},
        'revenue': get_revenue_summary(start, end),
        'orders': get_orders_summary(start, end),
        'menu_performance': get_menu_performance(start, end),
        'inventory': get_inventory_summary(start, end),
        'staff': get_staff_summary(start, end),
        'kitchen': get_kitchen_summary(start, end),
        'customer_feedback': get_feedback_summary(),
    }
