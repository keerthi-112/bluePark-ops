from django.contrib import admin
from .models import Category, Menu

from inventory.models import RecipeItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order')
    prepopulated_fields = {'slug': ('name',)}


class RecipeItemInline(admin.TabularInline):
    """Lets a Manager define this dish's ingredient BOM right from its
    own admin page -- inventory deducts stock against this on order."""
    model = RecipeItem
    extra = 1


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'category', 'price', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('item_name',)
    inlines = [RecipeItemInline]
