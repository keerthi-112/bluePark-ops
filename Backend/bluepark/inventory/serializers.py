from rest_framework import serializers

from .models import Ingredient, StockMovement, Supplier


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_info']


class IngredientSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.BooleanField(read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True, default=None)

    class Meta:
        model = Ingredient
        fields = [
            'id', 'name', 'unit', 'current_stock', 'reorder_threshold',
            'cost_per_unit', 'supplier', 'supplier_name', 'is_low_stock',
        ]


class StockMovementSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)

    class Meta:
        model = StockMovement
        fields = ['id', 'ingredient', 'ingredient_name', 'quantity_delta', 'reason', 'reference_order', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']


class CreateStockMovementSerializer(serializers.Serializer):
    ingredient = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    quantity_delta = serializers.DecimalField(max_digits=10, decimal_places=2)
    reason = serializers.ChoiceField(choices=StockMovement.REASON_CHOICES)
