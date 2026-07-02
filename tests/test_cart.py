from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from orders.models import CartItem
from products.models import Product
from users.models import MyUser

pytestmark = pytest.mark.django_db

CART_URL = '/api/cart/'
ITEMS_URL = '/api/cart/items/'


# ------------------------------------------------------------
# Проверка /api/cart/
# ------------------------------------------------------------
def test_cart_requires_auth(api_client: APIClient) -> None:
    """Корзина доступна только авторизованному пользователю."""
    response = api_client.get(CART_URL)

    assert response.status_code == 401


def test_cart_shows_items_and_total(
    auth_client: APIClient, product: Product
) -> None:
    """Сводка корзины отдаёт позиции и итоговую сумму."""
    auth_client.post(ITEMS_URL, {'product': product.id, 'quantity': 2})

    response = auth_client.get(CART_URL)

    assert response.status_code == 200
    assert len(response.data['items']) == 1
    assert Decimal(response.data['total_price']) == product.price * 2


# ------------------------------------------------------------
# Проверка /api/cart/items/
# ------------------------------------------------------------
def test_items_requires_auth(api_client: APIClient) -> None:
    """Позиции корзины недоступны анониму."""
    response = api_client.get(ITEMS_URL)

    assert response.status_code == 401


def test_add_item_default_quantity(
    auth_client: APIClient, user: MyUser, product: Product
) -> None:
    """Товар без количества добавляется в одном экземпляре."""
    response = auth_client.post(ITEMS_URL, {'product': product.id})

    assert response.status_code == 201
    item = CartItem.objects.get(user=user, product=product)
    assert item.quantity == 1


def test_add_same_product_increments(
    auth_client: APIClient, user: MyUser, product: Product
) -> None:
    """Повторное добавление того же товара суммирует количество."""
    auth_client.post(ITEMS_URL, {'product': product.id, 'quantity': 2})
    auth_client.post(ITEMS_URL, {'product': product.id, 'quantity': 3})

    item = CartItem.objects.get(user=user, product=product)
    assert item.quantity == 5
    assert CartItem.objects.filter(user=user, product=product).count() == 1


def test_add_more_than_stock_fails(
    auth_client: APIClient, product: Product
) -> None:
    """Нельзя положить в корзину больше, чем есть на складе."""
    response = auth_client.post(
        ITEMS_URL, {'product': product.id, 'quantity': product.in_stock + 1}
    )

    assert response.status_code == 400
    assert CartItem.objects.count() == 0


def test_user_sees_only_own_items(
    auth_client: APIClient, product: Product
) -> None:
    """Пользователь видит только свои позиции корзины."""
    stranger = MyUser.objects.create_user(
        username='stranger', email='s@test.com', password='StrongPass123!'
    )
    CartItem.objects.create(user=stranger, product=product, quantity=1)

    response = auth_client.get(ITEMS_URL)

    assert response.status_code == 200
    assert response.data == []


# ------------------------------------------------------------
# Проверка /api/cart/items/{id}/
# ------------------------------------------------------------
def test_update_item_quantity(
    auth_client: APIClient, user: MyUser, product: Product
) -> None:
    """Количество позиции меняется через PATCH."""
    item = CartItem.objects.create(user=user, product=product, quantity=1)

    response = auth_client.patch(f'{ITEMS_URL}{item.id}/', {'quantity': 4})

    assert response.status_code == 200
    item.refresh_from_db()
    assert item.quantity == 4


def test_cannot_change_product_on_update(
    auth_client: APIClient, user: MyUser, product: Product
) -> None:
    """Товар в позиции нельзя сменить — поле read-only при PATCH."""
    other = Product.objects.create(
        title='Коврик',
        description='Коврик для мыши',
        price=Decimal('500.00'),
        in_stock=5,
    )
    item = CartItem.objects.create(user=user, product=product, quantity=1)

    response = auth_client.patch(
        f'{ITEMS_URL}{item.id}/', {'product': other.id}
    )

    assert response.status_code == 200
    item.refresh_from_db()
    assert item.product == product


def test_delete_item(
    auth_client: APIClient, user: MyUser, product: Product
) -> None:
    """Позицию можно удалить из корзины."""
    item = CartItem.objects.create(user=user, product=product, quantity=1)

    response = auth_client.delete(f'{ITEMS_URL}{item.id}/')

    assert response.status_code == 204
    assert not CartItem.objects.filter(id=item.id).exists()
