from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Регистрация модели User в интерфейсе администратора."""

    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
    )

    empty_value_display = 'Значение отсутствует'
    search_fields = ('username', 'email',)
    list_filter = ('username', 'email',)
