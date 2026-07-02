from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from products.models import Product
from users.models import MyUser


@pytest.fixture
def api_client() -> APIClient:
    """Неаутентифицированный клиент API."""
    return APIClient()


@pytest.fixture
def user(db: None) -> MyUser:
    """Обычный покупатель с деньгами на балансе."""
    return MyUser.objects.create_user(
        username='aslan',
        email='aslan@test.com',
        password='StrongPass123!',
        balance=Decimal('100000.00'),
    )


@pytest.fixture
def admin(db: None) -> MyUser:
    """Пользователь-администратор, управляющий товарами."""
    return MyUser.objects.create_user(
        username='boss',
        email='boss@test.com',
        password='StrongPass123!',
        is_staff=True,
    )


@pytest.fixture
def auth_client(api_client: APIClient, user: MyUser) -> APIClient:
    """Клиент, авторизованный под обычным пользователем."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client: APIClient, admin: MyUser) -> APIClient:
    """Клиент, авторизованный под администратором."""
    api_client.force_authenticate(user=admin)
    return api_client


@pytest.fixture
def product(db: None) -> Product:
    """Товар в наличии для тестов корзины и заказов."""
    return Product.objects.create(
        title='Наушники',
        description='Беспроводные наушники',
        price=Decimal('8999.00'),
        in_stock=10,
    )
