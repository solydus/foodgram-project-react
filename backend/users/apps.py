from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Юзеры и фоллоуверы'
    verbose_name_plural = 'Юзеры и фоллоуверы'
