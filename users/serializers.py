from decimal import Decimal
from typing import Any

from rest_framework import serializers

from users.models import MyUser
from users.validators import (
    normalize_username,
    validate_password,
    validate_unique_email,
    validate_unique_username,
)


class BaseUserSerializer(serializers.ModelSerializer):
    """Базовый класс для серализаторов User."""

    balance = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    def validate_email(self, email: str) -> str:
        """Приводит email к нижнему регистру."""
        return email.lower()


class RegistrationSerializer(BaseUserSerializer):
    """Регистрация нового пользователя по username и password и email."""

    password = serializers.CharField(
        help_text='Придумайте пароль',
        write_only=True,
        validators=(validate_password,),
    )
    password_repeat = serializers.CharField(
        help_text='Повторите пароль', write_only=True
    )
    email = serializers.EmailField(
        required=True,
        validators=(validate_unique_email,),
    )

    class Meta:
        model = MyUser
        fields = (
            'username',
            'password',
            'password_repeat',
            'email',
            'balance',
        )

    def validate_username(self, username: str) -> str:
        """Нормализует username и проверяет его уникальность."""
        username = normalize_username(username)
        validate_unique_username(username)
        return username

    def create(self, validated_data: dict[str, Any]) -> MyUser:
        """Создаёт пользователя с захэшированным паролем."""
        return MyUser.objects.create_user(**validated_data)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Проверка корректности ввода пароля."""
        password = attrs.get('password')
        repeat = attrs.pop('password_repeat', None)
        if password != repeat:
            raise serializers.ValidationError({
                'password_repeat': 'Пароли не совпадают.'
            })
        return attrs


class UpdateProfileSerializer(BaseUserSerializer):
    """Обновление данных личного профиля пользхователя.

    Кроме баланса и username.
    """

    username = serializers.CharField(read_only=True)

    class Meta:
        model = MyUser
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'balance',
        )


class AddToBalanceSerializer(serializers.Serializer):
    """Пополнение баланса: принимает сумму большую нуля."""

    amount = serializers.DecimalField(
        help_text='введите сумму для пополнения баланса',
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
    )
