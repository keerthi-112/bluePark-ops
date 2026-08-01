from django.urls import path

from . import views

urlpatterns = [
    path('kitchen/queue/', views.queue, name='kitchen_queue'),
]
