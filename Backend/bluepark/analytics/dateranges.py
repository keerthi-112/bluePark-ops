"""Single source of truth for parsing the dashboard's date-range filter
(?range=today|7d|30d|custom&start=YYYY-MM-DD&end=YYYY-MM-DD). Every
analytics section and both the page view and the API view call
resolve_range() so filter parsing never drifts between them."""

from datetime import datetime, time, timedelta

from django.utils import timezone

RANGE_TODAY = 'today'
RANGE_7D = '7d'
RANGE_30D = '30d'
RANGE_CUSTOM = 'custom'
VALID_RANGES = {RANGE_TODAY, RANGE_7D, RANGE_30D, RANGE_CUSTOM}

DEFAULT_RANGE = RANGE_7D


def _start_of_day(date_obj):
    return timezone.make_aware(datetime.combine(date_obj, time.min))


def _end_of_day(date_obj):
    return timezone.make_aware(datetime.combine(date_obj, time.max))


def _parse_date(value):
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None


def resolve_range(request):
    """Returns (start_datetime, end_datetime, range_key) -- end_datetime
    is inclusive of the whole end day. Falls back to DEFAULT_RANGE on
    anything invalid or missing rather than raising, since this drives
    dashboard rendering, not a mutation."""

    range_key = request.GET.get('range', DEFAULT_RANGE)
    if range_key not in VALID_RANGES:
        range_key = DEFAULT_RANGE

    today = timezone.localdate()

    if range_key == RANGE_TODAY:
        return _start_of_day(today), _end_of_day(today), range_key

    if range_key == RANGE_7D:
        return _start_of_day(today - timedelta(days=6)), _end_of_day(today), range_key

    if range_key == RANGE_30D:
        return _start_of_day(today - timedelta(days=29)), _end_of_day(today), range_key

    # custom
    start_date = _parse_date(request.GET.get('start'))
    end_date = _parse_date(request.GET.get('end'))
    if not start_date or not end_date or start_date > end_date:
        return _start_of_day(today - timedelta(days=6)), _end_of_day(today), RANGE_7D

    return _start_of_day(start_date), _end_of_day(end_date), range_key
