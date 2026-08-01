from rest_framework import serializers

from .models import Category, Menu


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'display_order']


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Menu
        fields = ['id', 'item_name', 'category', 'category_name', 'menuimg', 'description', 'price', 'is_available']


class AvailabilitySerializer(serializers.Serializer):
    is_available = serializers.BooleanField()
