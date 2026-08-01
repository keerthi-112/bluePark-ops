from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem, OrderStatusHistory


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_active', 'total', 'created_at')
    list_filter = ('is_active',)
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('from_status', 'to_status', 'changed_by', 'changed_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'order_type', 'total_amount', 'payment_status', 'placed_at')
    list_filter = ('status', 'order_type', 'payment_status')
    inlines = [OrderItemInline, OrderStatusHistoryInline]
