from django.contrib import admin

from orders.models import CartItem, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Позиции заказа внутри заказа."""

    model = OrderItem
    extra = 0


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Админка позиций корзины."""

    list_display = ('id', 'user', 'product', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админка заказов."""

    list_display = ('id', 'user', 'total_price', 'created_at')
    inlines = (OrderItemInline,)
