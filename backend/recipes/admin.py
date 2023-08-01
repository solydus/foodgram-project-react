from django.contrib import admin

from .models import FavoriteRecipe, IngredientsAmount, Recipe, ShoppingCart


class IngredientsAmountInline(admin.TabularInline):
    model = IngredientsAmount
    extra = 1
    min_num = 1
    autocomplete_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'display_tags',
                    'favorite_count', 'shopping_count')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author__username', 'author__last_name',
                     'author__first_name', 'tags__name')
    filter_vertical = ('tags',)
    inlines = (IngredientsAmountInline,)

    def favorite_count(self, obj):
        return obj.favorites.count()

    def shopping_count(self, obj):
        return obj.shopcarts.count()

    def display_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])

    favorite_count.short_description = 'В избранном'
    shopping_count.short_description = 'В списке покупок'
    display_tags.short_description = 'Теги'


@admin.register(IngredientsAmount)
class IngredientsAmountAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
