from django.urls import path

from . import api

urlpatterns = [
    path('summary/', api.AnalyticsSummaryView.as_view(), name='api_analytics_summary'),
]
