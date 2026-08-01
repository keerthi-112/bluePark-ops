from django.urls import path

from . import views

urlpatterns = [
    path('overview/', views.manager_overview, name='manager_overview'),
]
