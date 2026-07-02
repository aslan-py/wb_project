from rest_framework.exceptions import ValidationError

from products.models import Product


def validate_stock(product: Product, quantity: int) -> None:
    """Проверяет, что количество не превышает остаток товара на складе."""
    if quantity > product.in_stock:
        raise ValidationError(
            f'На складе только {product.in_stock} шт. '
            f'товара «{product.title}».'
        )
