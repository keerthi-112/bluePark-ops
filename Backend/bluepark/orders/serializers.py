from rest_framework import serializers

from menu.models import Menu

from .models import Cart, CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='menu_item.item_name', read_only=True)
    unit_price = serializers.DecimalField(source='menu_item.price', max_digits=8, decimal_places=2, read_only=True)
    subtotal = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'menu_item', 'item_name', 'unit_price', 'quantity', 'note', 'subtotal']
        read_only_fields = ['id']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'is_active', 'items', 'total']


class AddCartItemSerializer(serializers.Serializer):
    menu_item = serializers.PrimaryKeyRelatedField(queryset=Menu.objects.filter(is_available=True))
    quantity = serializers.IntegerField(min_value=1, default=1)
    note = serializers.CharField(required=False, allow_blank=True, max_length=250, default='')


class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='menu_item.item_name', read_only=True)
    subtotal = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'item_name', 'quantity', 'unit_price_at_order_time', 'note', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'order_type', 'total_amount', 'payment_status', 'payment_method',
            'delivery_address', 'phone', 'placed_at', 'items',
        ]
        read_only_fields = ['id', 'status', 'total_amount', 'payment_status', 'placed_at']


class CreateOrderSerializer(serializers.Serializer):
    order_type = serializers.ChoiceField(choices=Order.ORDER_TYPE_CHOICES, default=Order.ORDER_TYPE_DELIVERY)
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_METHOD_CHOICES, default=Order.PAYMENT_METHOD_COD)
    delivery_address = serializers.CharField(required=False, allow_blank=True, max_length=350, default='')
    phone = serializers.CharField(required=False, allow_blank=True, max_length=12, default='')


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
