from django.urls import path

from . import api

urlpatterns = [
    path('ask/', api.AskCopilotView.as_view(), name='api_ai_ask'),
]
