from django.utils import timezone

from .models import Attendance


def get_upcoming_shifts(employee):
    return employee.shifts.filter(end_time__gte=timezone.now()).order_by('start_time')


def clock_in(employee, shift=None):
    return Attendance.objects.create(employee=employee, shift=shift, check_in=timezone.now())


def clock_out(attendance):
    attendance.check_out = timezone.now()
    attendance.save(update_fields=['check_out'])
    return attendance
