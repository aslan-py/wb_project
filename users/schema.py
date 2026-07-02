from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from users.serializers import AddToBalanceSerializer

register_schema = extend_schema(
    summary='Регистрация пользователя',
    description='Создание нового аккаунта: username, email и пароль.',
)

login_schema = extend_schema(
    summary='Авторизация (получение токенов)',
    description='Возвращает пару JWT: access и refresh.',
)

refresh_schema = extend_schema(
    summary='Обновление access-токена',
    description='Выдаёт новый access-токен по refresh-токену.',
)

profile_schema = extend_schema_view(
    get=extend_schema(
        summary='Просмотр профиля',
        description='Данные текущего пользователя.',
    ),
    patch=extend_schema(
        summary='Редактирование профиля',
        description='Частичное обновление данных профиля.',
    ),
)

add_balance_schema = extend_schema(
    summary='Пополнение баланса',
    description='Пополняет баланс текущего пользователя',
    request=AddToBalanceSerializer,
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description='Обновлённый баланс пользователя.',
            examples=[
                OpenApiExample(
                    'Успех',
                    value={'balance': '1500.00'},
                    response_only=True,
                ),
            ],
        ),
    },
)
