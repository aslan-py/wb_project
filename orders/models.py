from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from products.models import Product


class CartItem(models.Model):
    """Строка корзины: чей товар, какой и в каком количестве."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Владелец корзины',
        on_delete=models.CASCADE,
        related_name='cart',
    )
    product = models.ForeignKey(
        Product,
        verbose_name='Товар',
        on_delete=models.CASCADE,
        related_name='cart_items',
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество',
        default=1,
        validators=(MinValueValidator(1),),
    )

    class Meta:
        verbose_name = 'Позиция корзины'
        verbose_name_plural = 'Позиции корзины'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'product'),
                name='unique_user_product',
            ),
        )

    def __str__(self) -> str:
        """Строковое представление позиции корзины."""
        return f'{self.product} x {self.quantity}'


class Order(models.Model):
    """Заказ пользователя, оформленный из корзины."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Покупатель',
        on_delete=models.CASCADE,
        related_name='orders',
    )
    total_price = models.DecimalField(
        verbose_name='Итоговая сумма заказа',
        max_digits=10,
        decimal_places=2,
    )
    created_at = models.DateTimeField(
        verbose_name='Дата оформления',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        """Строковое представление заказа."""
        return f'Заказ №{self.pk} от {self.user}'


class OrderItem(models.Model):
    """Позиция заказа со снимком цены на момент покупки."""

    order = models.ForeignKey(
        Order,
        verbose_name='Заказ',
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        Product,
        verbose_name='Товар',
        on_delete=models.PROTECT,
        related_name='order_items',
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=(MinValueValidator(1),),
    )
    price = models.DecimalField(
        verbose_name='Цена на момент покупки',
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self) -> str:
        """Строковое представление позиции заказа."""
        return f'{self.product} x {self.quantity}'
