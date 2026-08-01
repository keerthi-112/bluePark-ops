from django.urls import path

from . import api

urlpatterns = [
    path('auth/me/', api.MeView.as_view(), name='api_me'),
    path('accounts/staff/', api.StaffCreateView.as_view(), name='api_staff_create'),
]
