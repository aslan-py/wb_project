from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from users.models import MyUser

pytestmark = pytest.mark.django_db

REGISTER_URL = '/api/users/register/'
LOGIN_URL = '/api/users/auth/login/'
REFRESH_URL = '/api/users/auth/refresh/'
PROFILE_URL = '/api/users/me/'
ADD_BALANCE_URL = '/api/users/me/add-balance/'


# ------------------------------------------------------------
# Проверка /api/users/register/
# ------------------------------------------------------------
def test_register_creates_user(api_client: APIClient) -> None:
    """Регистрация возвращает 201 и создаёт пользователя."""
    response = api_client.post(
        REGISTER_URL,
        {
            'username': 'newbie',
            'email': 'newbie@test.com',
            'password': 'StrongPass123!',
            'password_repeat': 'StrongPass123!',
        },
    )

    assert response.status_code == 201
    assert MyUser.objects.filter(username__iexact='newbie').exists()


def test_register_password_mismatch(api_client: APIClient) -> None:
    """Разные пароли — регистрация отклоняется с 400."""
    response = api_client.post(
        REGISTER_URL,
        {
            'username': 'newbie',
            'email': 'newbie@test.com',
            'password': 'StrongPass123!',
            'password_repeat': 'OtherPass123!',
        },
    )

    assert response.status_code == 400
    assert not MyUser.objects.filter(username='newbie').exists()


def test_register_duplicate_email(api_client: APIClient, user: MyUser) -> None:
    """Повторный email отклоняется с 400, а не падает в 500."""
    response = api_client.post(
        REGISTER_URL,
        {
            'username': 'other',
            'email': user.email.upper(),
            'password': 'StrongPass123!',
            'password_repeat': 'StrongPass123!',
        },
    )

    assert response.status_code == 400
    assert 'email' in response.data


def test_register_duplicate_username_case_insensitive(
    api_client: APIClient, user: MyUser
) -> None:
    """Username в другом регистре считается занятым → 400."""
    response = api_client.post(
        REGISTER_URL,
        {
            'username': user.username.upper(),
            'email': 'fresh@test.com',
            'password': 'StrongPass123!',
            'password_repeat': 'StrongPass123!',
        },
    )

    assert response.status_code == 400
    assert 'username' in response.data


# ------------------------------------------------------------
# Проверка /api/users/auth/login/
# ------------------------------------------------------------
def test_login_returns_tokens(api_client: APIClient, user: MyUser) -> None:
    """Логин по логину и паролю выдаёт пару JWT-токенов."""
    response = api_client.post(
        LOGIN_URL,
        {'username': 'aslan', 'password': 'StrongPass123!'},
    )

    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data


# ------------------------------------------------------------
# Проверка /api/users/auth/refresh/
# ------------------------------------------------------------
def test_refresh_returns_new_access(
    api_client: APIClient, user: MyUser
) -> None:
    """По refresh-токену выдаётся новый access-токен."""
    tokens = api_client.post(
        LOGIN_URL,
        {'username': 'aslan', 'password': 'StrongPass123!'},
    ).data

    response = api_client.post(REFRESH_URL, {'refresh': tokens['refresh']})

    assert response.status_code == 200
    assert 'access' in response.data


# ------------------------------------------------------------
# Проверка /api/users/me/
# ------------------------------------------------------------
def test_profile_requires_auth(api_client: APIClient) -> None:
    """Без авторизации профиль недоступен."""
    response = api_client.get(PROFILE_URL)

    assert response.status_code == 401


def test_profile_get(auth_client: APIClient, user: MyUser) -> None:
    """Авторизованный пользователь видит свой профиль."""
    response = auth_client.get(PROFILE_URL)

    assert response.status_code == 200
    assert response.data['username'] == user.username


def test_profile_patch(auth_client: APIClient, user: MyUser) -> None:
    """Пользователь может изменить имя в профиле."""
    response = auth_client.patch(PROFILE_URL, {'first_name': 'Аслан'})

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.first_name == 'Аслан'


# ------------------------------------------------------------
# Проверка /api/users/me/add-balance/
# ------------------------------------------------------------
def test_add_balance(auth_client: APIClient, user: MyUser) -> None:
    """Пополнение баланса увеличивает счёт пользователя."""
    response = auth_client.post(ADD_BALANCE_URL, {'amount': '500.00'})

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.balance == Decimal('100500.00')


def test_add_balance_rejects_zero(auth_client: APIClient) -> None:
    """Пополнение на ноль — ошибка валидации."""
    response = auth_client.post(ADD_BALANCE_URL, {'amount': '0.00'})

    assert response.status_code == 400
