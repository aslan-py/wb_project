# WB Project — интернет-магазин на Django REST Framework

REST API интернет-магазина: пользователи с балансом, каталог товаров,
корзина и оформление заказов. Проект контейнеризирован (Docker + Docker
Compose), покрыт тестами и снабжён автогенерируемой документацией (Swagger- через drf-spectacular).  
Для удобства разорачивает  web интерфейс БД - Adminer

## Возможности

- **Пользователи** — регистрация, JWT-авторизация, профиль, личный баланс
  с пополнением. Нормализация и проверка уникальности `username`/`email`
  (без учёта регистра).
- **Товары** — CRUD; читают все, создавать/менять/удалять может только
  администратор. Уникальность пары «название + описание».
- **Корзина** — добавление товара, изменение количества, удаление,
  просмотр сводки с итоговой суммой. Проверка остатков на складе.
- **Заказы** — оформление из корзины: проверка баланса и склада, списание
  средств и остатков, очистка корзины, уведомление в лог.
- **Документация** — Swagger UI сгенерированные из кода.
- **Админка** — управление пользователями и их ролями.

## Стек

- Python 3.12
- Django 6
- Django REST Framework
- SimpleJWT
- zxcvbn(проверка сложности пароля) 
- менеджер пакетов uv
- линтер ruff

## Структура проекта

```
wb_project/
├── api/                 # корневой роутер API и документация
│   ├── schema.py        # хук простановки тегов в Swagger по URL
│   └── urls.py          # сборка всех маршрутов /api/ + docs
├── config/              # конфигурация проекта
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/               # пользователи: регистрация, профиль, баланс
│   ├── models.py        # кастомная модель MyUser
│   ├── serializers.py
│   ├── views.py
│   ├── validators.py    # проверка пароля, email, username
│   ├── services.py      # бизнес-логика (пополнение баланса)
│   ├── schema.py        # описания эндпоинтов для Swagger
│   ├── admin.py
│   └── urls.py
├── products/            # товары: CRUD, права администратора
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py   # IsAdminOrReadOnly
│   ├── validators.py
│   ├── schema.py
│   └── urls.py
├── orders/              # корзина и заказы
│   ├── models.py        # CartItem, Order, OrderItem
│   ├── serializers.py
│   ├── views.py
│   ├── services.py      # оформление заказа (checkout)
│   ├── validators.py    # проверка остатков на складе
│   ├── schema.py
│   └── urls.py
├── tests/               # pytest-тесты (users, products, cart, checkout)
│   ├── conftest.py
│   ├── test_users.py
│   ├── test_products.py
│   ├── test_cart.py
│   └── test_checkout.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt     # зависимости для pip
├── pyproject.toml       # зависимости для uv
├── uv.lock
├── manage.py
└── .env
```

## Запуск через Docker (рекомендуется)

Единственное требование — установленный Docker. Ни Python, ни менеджеры
пакетов на хосте не нужны.

```bash
docker compose up --build
```

При старте контейнер собирает статику, применяет миграции и поднимает
приложение на gunicorn. Сервисы:

- API — http://localhost:8000/api/
- Swagger — http://localhost:8000/api/docs/
- Админка — http://localhost:8000/admin/
- Adminer (веб-клиент БД) — http://localhost:8080/  
(Для входа в Adminer: Движок-`PostgreSQL`, Сервер-`wb_postgres_db`,Имя пользователя-`postgres`, Пароль-`postgres`,База данных-`wb`)

Создать суперпользователя для входа в админку:

```bash
docker compose exec web uv run python manage.py createsuperuser
```
Посмотреть отбивку (успешный лог создания заказа):

```bash
docker compose logs web --tail 3
```
## Локальный запуск (без Docker)

Приложение использует SQLite при `DJANGO_DEBUG=True`.

**Через uv:**

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

**Через pip:**

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Переменные окружения (.env)

```dotenv
SECRET_KEY=<секретный ключ Django>
DJANGO_DEBUG=True                 # True — SQLite, False — PostgreSQL
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,[::1]

DB_NAME=wb
DB_USER=postgres
DB_PASSWORD=postgres
DB_PORT=5432
```

В Docker `DJANGO_DEBUG` и `DB_HOST` переопределяются в `docker-compose.yml`,
чтобы приложение работало на PostgreSQL.

## Основные эндпоинты

| Метод | URL | Назначение |
|-------|-----|------------|
| POST | `/api/users/register/` | Регистрация |
| POST | `/api/users/auth/login/` | Получение JWT-токенов |
| POST | `/api/users/auth/refresh/` | Обновление access-токена |
| GET/PATCH | `/api/users/me/` | Профиль |
| POST | `/api/users/me/add-balance/` | Пополнение баланса |
| GET/POST | `/api/products/` | Список / создание товаров |
| GET/PATCH/DELETE | `/api/products/{id}/` | Товар по id |
| GET | `/api/cart/` | Сводка корзины |
| GET/POST | `/api/cart/items/` | Позиции корзины |
| GET/PATCH/DELETE | `/api/cart/items/{id}/` | Позиция по id |
| POST | `/api/cart/checkout/` | Оформление заказа |

Полное описание — в Swagger: `/api/docs/`.

## Тесты

```bash
uv run pytest            # или: pytest
```

## Линтер

```bash
uv run ruff check
```
