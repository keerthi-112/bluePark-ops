from django.contrib import admin

from .models import Ingredient, RecipeItem, StockMovement, Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_info')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'current_stock', 'reorder_threshold', 'is_low_stock', 'supplier')
    list_filter = ('unit', 'supplier')

    @admin.display(boolean=True, description='Low stock')
    def is_low_stock(self, obj):
        return obj.is_low_stock


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'quantity_delta', 'reason', 'reference_order', 'created_by', 'created_at')
    list_filter = ('reason',)
    readonly_fields = ('created_at',)
