from django.urls import path

from . import api

urlpatterns = [
    path('employees/', api.EmployeeListCreateView.as_view(), name='api_employees'),
    path('shifts/', api.ShiftListCreateView.as_view(), name='api_shifts'),
    path('shifts/mine/', api.MyShiftsView.as_view(), name='api_my_shifts'),
    path('attendance/clock-in/', api.ClockInView.as_view(), name='api_clock_in'),
    path('attendance/<int:pk>/clock-out/', api.ClockOutView.as_view(), name='api_clock_out'),
]
