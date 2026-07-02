from rest_framework import serializers

from products.models import Product
from products.validators import normalize_text


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор товара для CRUD-операций."""

    class Meta:
        model = Product
        fields = (
            'id',
            'title',
            'description',
            'price',
            'in_stock',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'created_at',
            'updated_at',
        )

    def validate_title(self, value: str) -> str:
        """Название товара с большой буквы и убираем левый пробел."""
        return normalize_text(value)

    def validate_description(self, value: str) -> str:
        """Описание товара с большой буквы и убираем левый пробел."""
        return normalize_text(value)
