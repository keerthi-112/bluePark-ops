from django.urls import path

from . import views

urlpatterns = [
    path('inventory/', views.dashboard, name='inventory_dashboard'),
]
