from django.contrib import admin

from .models import Attendance, Employee, Shift


class ShiftInline(admin.TabularInline):
    model = Shift
    extra = 0


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'hire_date')
    search_fields = ('user__username', 'position')
    inlines = [ShiftInline]


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('employee', 'start_time', 'end_time')
    list_filter = ('employee',)
    date_hierarchy = 'start_time'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'shift', 'check_in', 'check_out')
