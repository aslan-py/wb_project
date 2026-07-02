from django.contrib import admin

from products.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Админка товаров."""

    list_display = ('id', 'title', 'price', 'in_stock', 'created_at')
    list_display_links = ('id', 'title')
    search_fields = ('title',)
