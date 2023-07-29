from django.contrib import admin

from recipes.models import (Ingredient,
                            Tag,
                            Recipe,
                            Recipe_ingredient,
                            Favorite,
                            Shopping_cart)


class RecipeTagInline(admin.TabularInline):
    model = Recipe.tags.through


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    ''' Админка Игридиента '''

    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    ''' Админка Тэгов '''

    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    ''' Админка рецептов '''

    list_display = ('pk', 'name', 'author', 'in_favorites')
    readonly_fields = ('in_favorites',)
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
    inlines = [RecipeTagInline]

    @admin.display(description='В избранном')
    def in_favorites(self, obj):
        return obj.favorite_recipe.count()


@admin.register(Recipe_ingredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    ''' Отображение ингридиентов в рецепте '''

    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    list_editable = ('recipe', 'ingredient', 'amount')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    ''' Избранные рецепты '''

    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe')


@admin.register(Shopping_cart)
class ShoppingCartAdmin(admin.ModelAdmin):
    ''' Админка Корзины рецептов '''

    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe')
