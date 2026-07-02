import logging
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.core.mail import send_mail
from django.db import transaction
from rest_framework.exceptions import ValidationError

from orders.models import CartItem, Order, OrderItem
from products.models import Product

logger = logging.getLogger(__name__)


def _notify_order_created(order: Order) -> None:
    """Логирует оформление заказа и шлёт письмо покупателю."""
    logger.info(
        'Заказ №%s оформлен пользователем %s на сумму %s',
        order.pk,
        order.user,
        order.total_price,
    )
    send_mail(
        subject=f'Заказ №{order.pk} оформлен',
        message=f'Ваш заказ на сумму {order.total_price} успешно оформлен.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=(order.user.email,),
        fail_silently=True,
    )


@transaction.atomic
def checkout(user: AbstractBaseUser) -> Order:
    """Оформляет заказ из корзины: проверки, списания, очистка корзины."""
    items = list(CartItem.objects.filter(user=user).select_related('product'))
    if not items:
        raise ValidationError('Корзина пуста.')

    products = Product.objects.select_for_update().in_bulk([
        item.product_id for item in items
    ])

    total = Decimal('0.00')
    for item in items:
        product = products[item.product_id]
        if product.in_stock < item.quantity:
            raise ValidationError(
                f'Недостаточно товара «{product.title}» на складе.'
            )
        total += product.price * item.quantity

    if user.balance < total:
        raise ValidationError('Недостаточно средств на балансе.')

    order = Order.objects.create(user=user, total_price=total)
    order_items = []
    for item in items:
        product = products[item.product_id]
        product.in_stock -= item.quantity
        product.save(update_fields=('in_stock',))
        order_items.append(
            OrderItem(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price,
            )
        )
    OrderItem.objects.bulk_create(order_items)

    user.balance -= total
    user.save(update_fields=('balance',))
    CartItem.objects.filter(user=user).delete()

    _notify_order_created(order)
    return order
