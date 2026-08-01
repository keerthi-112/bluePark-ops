from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from core.constants import ROLE_ADMIN, ROLE_MANAGER

from .dateranges import resolve_range
from .services import build_summary_payload

MANAGER_ROLES = {ROLE_MANAGER, ROLE_ADMIN}


@login_required
def dashboard(request):
    role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if role not in MANAGER_ROLES:
        raise PermissionDenied('Analytics is only available to Manager/Admin.')

    # Initial paint uses the default range (7d, i.e. no query params) --
    # the exact same payload shape the API returns, since the page's JS
    # re-fetches from /api/v1/analytics/summary/ on every filter change.
    start, end, range_key = resolve_range(request)
    initial_data = build_summary_payload(start, end, range_key)

    return render(request, 'analytics_dashboard.html', {'initial_data': initial_data})
