from django.contrib import admin

from .models import User, Subscribe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    like_recipe = ('id', 'username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email')


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    like_recipe = ('id', 'user', 'author')
    list_filter = ('user',)
    search_fields = ('user__username', 'author__username')
