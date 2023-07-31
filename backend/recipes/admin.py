from django.contrib import admin

from .models import (Favorite, Follow, Ingredient, IngredientRecipe, Recipe,
                     ShoppingList, Tag)

admin.site.empty_value_display = 'Значение отсутствует'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    min_num = 1
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'get_favorites',
        'get_tags',
        'get_ingredients',
    )
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name',)
    inlines = (IngredientRecipeInline,)

    def get_favorites(self, obj):
        return obj.favorites.count()

    get_favorites.short_description = (
        'Количество добавлений рецепта в избранное'
    )

    def get_tags(self, obj):
        return ', '.join((tag.name for tag in obj.tags.all()))

    get_tags.short_description = 'Тег или список тегов'

    def get_ingredients(self, obj):
        return ', '.join(
            (ingredient.name for ingredient in obj.ingredients.all())
        )

    get_ingredients.short_description = 'Ингридиенты'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'recipe', 'amount')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
