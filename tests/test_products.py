from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from products.models import Product

pytestmark = pytest.mark.django_db

PRODUCTS_URL = '/api/products/'

NEW_PRODUCT = {
    'title': 'Мышка',
    'description': 'Игровая мышка',
    'price': '1500.00',
    'in_stock': 5,
}


# ------------------------------------------------------------
# Проверка /api/products/
# ------------------------------------------------------------
def test_list_products_allows_anonymous(
    api_client: APIClient, product: Product
) -> None:
    """Список товаров доступен без авторизации."""
    response = api_client.get(PRODUCTS_URL)

    assert response.status_code == 200
    assert len(response.data) == 1


def test_admin_creates_product(admin_client: APIClient) -> None:
    """Администратор создаёт товар."""
    response = admin_client.post(PRODUCTS_URL, NEW_PRODUCT)

    assert response.status_code == 201
    assert Product.objects.filter(title='Мышка').exists()


def test_admin_cannot_create_duplicate(
    admin_client: APIClient, product: Product
) -> None:
    """Дубль пары title+description отклоняется с 400, а не падает."""
    response = admin_client.post(
        PRODUCTS_URL,
        {
            'title': product.title.lower(),
            'description': product.description.lower(),
            'price': '2000.00',
            'in_stock': 3,
        },
    )

    assert response.status_code == 400
    assert 'non_field_errors' in response.data
    assert Product.objects.filter(title=product.title).count() == 1


def test_regular_user_cannot_create(auth_client: APIClient) -> None:
    """Обычному пользователю создание товара запрещено (403)."""
    response = auth_client.post(PRODUCTS_URL, NEW_PRODUCT)

    assert response.status_code == 403
    assert not Product.objects.filter(title='Мышка').exists()


def test_anonymous_cannot_create(api_client: APIClient) -> None:
    """Анонимный пользователь не может создавать товары."""
    response = api_client.post(PRODUCTS_URL, NEW_PRODUCT)

    assert response.status_code in (401, 403)


# ------------------------------------------------------------
# Проверка /api/products/{id}/
# ------------------------------------------------------------
def test_retrieve_product(api_client: APIClient, product: Product) -> None:
    """Отдельный товар можно получить по id."""
    response = api_client.get(f'{PRODUCTS_URL}{product.id}/')

    assert response.status_code == 200
    assert response.data['title'] == product.title


def test_admin_updates_product(
    admin_client: APIClient, product: Product
) -> None:
    """Администратор меняет цену товара через PATCH."""
    response = admin_client.patch(
        f'{PRODUCTS_URL}{product.id}/', {'price': '9999.00'}
    )

    assert response.status_code == 200
    product.refresh_from_db()
    assert product.price == Decimal('9999.00')


def test_admin_deletes_product(
    admin_client: APIClient, product: Product
) -> None:
    """Администратор удаляет товар."""
    response = admin_client.delete(f'{PRODUCTS_URL}{product.id}/')

    assert response.status_code == 204
    assert not Product.objects.filter(id=product.id).exists()
