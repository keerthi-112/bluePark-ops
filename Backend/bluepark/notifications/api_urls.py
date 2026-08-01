from django.urls import path

from . import api

urlpatterns = [
    path('', api.NotificationListView.as_view(), name='api_notifications'),
    path('<int:pk>/read/', api.NotificationMarkReadView.as_view(), name='api_notification_read'),
]
