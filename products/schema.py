from drf_spectacular.utils import extend_schema, extend_schema_view

product_schema = extend_schema_view(
    list=extend_schema(
        summary='Список товаров',
        description='Доступно всем.',
    ),
    retrieve=extend_schema(
        summary='Карточка товара',
        description='Доступно всем.',
    ),
    create=extend_schema(
        summary='Создание товара',
        description='Только для администратора.',
    ),
    update=extend_schema(
        summary='Полное обновление товара',
        description='Только для администратора.',
    ),
    partial_update=extend_schema(
        summary='Частичное обновление товара',
        description='Только для администратора.',
    ),
    destroy=extend_schema(
        summary='Удаление товара',
        description='Только для администратора.',
    ),
)
