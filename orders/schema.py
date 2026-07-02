from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from orders.serializers import OrderSerializer

cart_schema = extend_schema(
    summary='Просмотр корзины',
    description=(
        'Все позиции корзины и итоговая сумма.\n\nТолько зарегистрированным.'
    ),
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description='Позиции корзины и общая стоимость.',
            examples=[
                OpenApiExample(
                    'Корзина',
                    value={
                        'items': [
                            {
                                'id': 1,
                                'product': 1,
                                'product_title': 'Наушники',
                                'product_price': '8999.00',
                                'quantity': 2,
                            },
                        ],
                        'total_price': '17998.00',
                    },
                    response_only=True,
                ),
            ],
        ),
    },
)

cart_item_schema = extend_schema_view(
    list=extend_schema(
        summary='Список позиций корзины.',
        description=(
            'Все товары в корзине пользователя.\n\nТолько зарегистрированным.'
        ),
    ),
    create=extend_schema(
        summary='Добавление товара в корзину',
        description=(
            'Создаёт позицию или увеличивает количество.\n\n'
            'Только зарегистрированным.'
        ),
    ),
    retrieve=extend_schema(
        summary='Позиция корзины',
        description=(
            'Одна позиция корзины по id.\n\nТолько зарегистрированным.'
        ),
    ),
    partial_update=extend_schema(
        summary='Изменение количества',
        description=(
            'Меняет количество товара в позиции.\n\nТолько зарегистрированным.'
        ),
    ),
    destroy=extend_schema(
        summary='Удаление позиции',
        description=(
            'Убирает товар из корзины.\n\nТолько зарегистрированным.'
        ),
    ),
)

checkout_schema = extend_schema(
    summary='Оформление заказа',
    description=(
        'Создаёт заказ из корзины и очищает её.\n\nТолько зарегистрированным.'
    ),
    request=None,
    responses={201: OrderSerializer},
)
