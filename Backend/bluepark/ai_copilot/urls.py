from django.urls import path

from . import views

urlpatterns = [
    path('ai-copilot/', views.chat, name='ai_copilot_chat'),
]
