from django.urls import path

from . import views

urlpatterns = [
    path('staff/', views.dashboard, name='staff_dashboard'),
    path('staff/my-shifts/', views.my_shifts, name='my_shifts'),
]
