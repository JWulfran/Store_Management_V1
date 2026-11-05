from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'category', 'purchase_price', 'selling_price', 'stock', 'is_active')
    search_fields = ('sku', 'name', 'description')
    list_filter = ('category', 'is_active')
    ordering = ('name',)
    list_editable = ('purchase_price', 'selling_price', 'stock', 'is_active')
    readonly_fields = ('created_at', 'updated_at')