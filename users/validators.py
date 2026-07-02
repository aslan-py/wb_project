from rest_framework.serializers import ValidationError
from zxcvbn import zxcvbn

from users.models import MyUser


def validate_unique_email(email: str) -> str:
    """Проверяет, что email ещё не занят (без учёта регистра)."""
    if MyUser.objects.filter(email__iexact=email).exists():
        raise ValidationError('Пользователь с таким email уже существует.')
    return email


def normalize_username(username: str) -> str:
    """Убирает пробелы по краям."""
    return username.strip()


def validate_unique_username(username: str) -> str:
    """Проверяет, что username ещё не занят (без учёта регистра)."""
    if MyUser.objects.filter(username__iexact=username).exists():
        raise ValidationError('Пользователь с таким username уже занят.')
    return username


def validate_password(password: str) -> str:
    """Проверяем уровернь сложности пароля."""
    results = zxcvbn(password)
    if results['score'] < 3:
        feedback = results.get('feedback', {}).get(
            'suggestions', ['Пароль слишком простой']
        )
        raise ValidationError(f'Пароль слишком слабый. {". ".join(feedback)}')
    return password
