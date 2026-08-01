from django.urls import path

from . import views

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('waiting', views.waiting, name='waiting'),
]
