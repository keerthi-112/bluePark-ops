from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils import timezone

from core.constants import ROLE_ADMIN, ROLE_MANAGER

from . import services
from .models import Employee, Shift

MANAGER_ROLES = {ROLE_MANAGER, ROLE_ADMIN}


@login_required
def dashboard(request):
    role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if role not in MANAGER_ROLES:
        raise PermissionDenied('Staff management is only available to Manager/Admin.')

    employees = Employee.objects.select_related('user', 'user__profile').order_by('user__username')
    upcoming_shifts = Shift.objects.select_related('employee__user').filter(end_time__gte=timezone.now()).order_by('start_time')[:20]

    return render(request, 'staff_dashboard.html', {
        'employees': employees,
        'upcoming_shifts': upcoming_shifts,
    })


@login_required
def my_shifts(request):
    employee = getattr(request.user, 'employee', None)
    shifts = services.get_upcoming_shifts(employee) if employee else []
    open_attendance = employee.attendance.filter(check_out__isnull=True).first() if employee else None
    return render(request, 'my_shifts.html', {'employee': employee, 'shifts': shifts, 'open_attendance': open_attendance})
