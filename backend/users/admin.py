from django.contrib import admin

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    recipe_lover = ('id', 'username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email')


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    recipe_lover = ('id', 'user', 'author')
    list_filter = ('user',)
    search_fields = ('user__username', 'author__username')
