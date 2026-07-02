from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import MyUser


@admin.register(MyUser)
class MyUserAdmin(UserAdmin):
    """Управление пользователями: роли (staff/superuser) и баланс."""

    list_display = (
        'username',
        'email',
        'is_staff',
        'is_superuser',
        'balance',
    )
    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
    )
    fieldsets = UserAdmin.fieldsets + (('Баланс', {'fields': ('balance',)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('email',)}),
    )
