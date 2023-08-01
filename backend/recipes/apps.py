from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    verbose_name = 'Рецепт'
    verbose_name_plural = 'Рецепты'
