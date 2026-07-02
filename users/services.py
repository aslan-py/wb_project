from decimal import Decimal

from users.models import MyUser


def top_up_balance(user: MyUser, amount: Decimal) -> MyUser:
    """Пополняет баланс пользователя на указанную сумму."""
    user.balance += amount
    user.save()
    return user
