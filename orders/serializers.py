from rest_framework import serializers

from orders.models import CartItem, Order, OrderItem
from orders.validators import validate_stock


class CartItemSerializer(serializers.ModelSerializer):
    """Позиция корзины: товар на запись, его данные — на чтение."""

    product_title = serializers.CharField(
        source='product.title', read_only=True
    )
    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = CartItem
        fields = (
            'id',
            'product',
            'product_title',
            'product_price',
            'quantity',
        )

    def get_fields(self) -> dict:
        """При изменении позиции товар менять нельзя — только количество."""
        fields = super().get_fields()
        if self.instance is not None:
            fields['product'].read_only = True
        return fields

    def validate(self, attrs: dict) -> dict:
        """Не даёт заказать больше товара, чем есть на складе."""
        product = attrs.get('product') or self.instance.product
        if self.instance is None:
            quantity = attrs.get('quantity', 1)
            existing = CartItem.objects.filter(
                user=self.context['request'].user, product=product
            ).first()
            if existing is not None:
                quantity += existing.quantity
        else:
            quantity = attrs.get('quantity', self.instance.quantity)
        validate_stock(product, quantity)
        return attrs

    def create(self, validated_data: dict) -> CartItem:
        """Добавляет товар в корзину или увеличивает его количество."""
        user = validated_data['user']
        product = validated_data['product']
        quantity = validated_data.get('quantity', 1)
        item, created = CartItem.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': quantity},
        )
        if not created:
            item.quantity += quantity
            item.save(update_fields=('quantity',))
        return item


class OrderItemSerializer(serializers.ModelSerializer):
    """Позиция заказа со снимком цены на момент покупки."""

    product_title = serializers.CharField(
        source='product.title', read_only=True
    )

    class Meta:
        model = OrderItem
        fields = (
            'id',
            'product',
            'product_title',
            'quantity',
            'price',
        )


class OrderSerializer(serializers.ModelSerializer):
    """Заказ с позициями (только чтение)."""

    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'total_price',
            'created_at',
            'items',
        )
