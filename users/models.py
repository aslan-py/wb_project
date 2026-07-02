from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class MyUser(AbstractUser):
    """Перепопределяем стандартный User класс."""

    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
    )
    balance = models.DecimalField(
        verbose_name='Баланс пользователя',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=(MinValueValidator(Decimal('0.00')),),
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
