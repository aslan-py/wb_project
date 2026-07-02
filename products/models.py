from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    """Модель товаров."""

    title = models.CharField(
        verbose_name='Название товара',
        max_length=255,
    )
    description = models.TextField(
        verbose_name='Описание товара',
    )
    price = models.DecimalField(
        verbose_name='Цена товара',
        max_digits=10,
        decimal_places=2,
        validators=(MinValueValidator(Decimal('1.00')),),
    )
    in_stock = models.PositiveIntegerField(
        verbose_name='Количество товара на складе',
        default=1,
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата обновления',
        auto_now=True,
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('-created_at',)
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'description'),
                name='unique_product_title_description',
            ),
        )

    def __str__(self) -> str:
        """Строковое представление товара."""
        return self.title
