from django.urls import path

from . import api

urlpatterns = [
    path('queue/', api.KitchenQueueView.as_view(), name='api_kitchen_queue'),
]
