from django.urls import path

from . import api

urlpatterns = [
    path('categories/', api.CategoryListCreateView.as_view(), name='api_menu_categories'),
    path('items/', api.MenuItemListCreateView.as_view(), name='api_menu_items'),
    path('items/<int:pk>/', api.MenuItemDetailView.as_view(), name='api_menu_item_detail'),
    path('items/<int:pk>/availability/', api.MenuItemAvailabilityView.as_view(), name='api_menu_item_availability'),
]
