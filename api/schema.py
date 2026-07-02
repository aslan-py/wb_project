from typing import Any

# Первый сегмент пути после /api/ -> человекочитаемое имя группы.
URL_TAGS = {
    'users': 'Пользователи',
    'products': 'Товары',
    'cart': 'Корзина',
}


def assign_tags_by_url(
    result: dict[str, Any],
    generator: Any,
    request: Any,
    public: bool,
) -> dict[str, Any]:
    """Проставляет тег группы каждой операции по сегменту URL."""
    for path, methods in result['paths'].items():
        parts = path.strip('/').split('/')
        segment = parts[1] if len(parts) > 1 else ''
        tag = URL_TAGS.get(segment)
        if tag:
            for operation in methods.values():
                operation['tags'] = [tag]
    return result
