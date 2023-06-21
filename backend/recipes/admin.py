from django.contrib import admin
from django.db.models import Count

from .models import Favorite, Ingredient, IngredientInRecipe, Recipe, ShoppingCart, Tag


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = ('id', 'name', 'author_name', 'tags_list', 'total_likes')
    list_filter = ('name', 'author__username', 'tags')

    def tags_list(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    def author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username

    def total_likes(self, obj):
        return obj.favorites.count()

    tags_list.short_description = 'Тэги'
    author_name.short_description = 'Автор'
    total_likes.short_description = 'Лайки'


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color')
    list_filter = ('name',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'recipe_lover')
    list_filter = ('recipe_lover',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('cart_owner', 'recipe')
    list_filter = ('cart_owner',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
