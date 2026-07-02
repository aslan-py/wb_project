from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from orders.models import CartItem, Order, OrderItem
from products.models import Product
from users.models import MyUser

pytestmark = pytest.mark.django_db

CHECKOUT_URL = '/api/cart/checkout/'
ITEMS_URL = '/api/cart/items/'


# ------------------------------------------------------------
# Проверка /api/cart/checkout/
# ------------------------------------------------------------
def test_checkout_requires_auth(api_client: APIClient) -> None:
    """Оформление заказа недоступно анониму."""
    response = api_client.post(CHECKOUT_URL)

    assert response.status_code == 401


def test_checkout_success(
    auth_client: APIClient, user: MyUser, product: Product
) -> None:
    """Оформление: заказ создан, списания и очистка корзины."""
    auth_client.post(ITEMS_URL, {'product': product.id, 'quantity': 2})
    balance_before = user.balance

    response = auth_client.post(CHECKOUT_URL)

    assert response.status_code == 201
    order = Order.objects.get(user=user)
    assert order.total_price == product.price * 2

    item = OrderItem.objects.get(order=order)
    assert item.quantity == 2
    assert item.price == product.price

    user.refresh_from_db()
    product.refresh_from_db()
    assert user.balance == balance_before - product.price * 2
    assert product.in_stock == 8
    assert CartItem.objects.filter(user=user).count() == 0


def test_checkout_empty_cart(auth_client: APIClient, user: MyUser) -> None:
    """Оформление пустой корзины отклоняется с 400."""
    response = auth_client.post(CHECKOUT_URL)

    assert response.status_code == 400
    assert Order.objects.filter(user=user).count() == 0


def test_checkout_insufficient_balance(
    api_client: APIClient, product: Product
) -> None:
    """Нехватка денег: заказ не создаётся, списаний нет."""
    poor = MyUser.objects.create_user(
        username='poor',
        email='poor@test.com',
        password='StrongPass123!',
        balance=Decimal('100.00'),
    )
    api_client.force_authenticate(user=poor)
    CartItem.objects.create(user=poor, product=product, quantity=1)

    response = api_client.post(CHECKOUT_URL)

    assert response.status_code == 400
    assert Order.objects.count() == 0
    poor.refresh_from_db()
    product.refresh_from_db()
    assert poor.balance == Decimal('100.00')
    assert product.in_stock == 10
    assert CartItem.objects.filter(user=poor).count() == 1


def test_checkout_insufficient_stock(
    auth_client: APIClient, user: MyUser, product: Product
) -> None:
    """Нехватка склада: заказ не создаётся."""
    CartItem.objects.create(
        user=user, product=product, quantity=product.in_stock + 5
    )

    response = auth_client.post(CHECKOUT_URL)

    assert response.status_code == 400
    assert Order.objects.count() == 0
    product.refresh_from_db()
    assert product.in_stock == 10
