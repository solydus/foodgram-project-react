from django.contrib import admin

from .models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                     RecipeTag, ShoppingList, Tag)


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1


class TagInline(admin.TabularInline):
    model = RecipeTag
    min_num = 1


class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color", "slug")
    search_fields = ("name", "slug")
    empty_value_display = "-пусто-"


class IngredientAdmin(admin.ModelAdmin):
    list_dispay = ("id", "name", "measurement_unit")
    search_fields = ("name",)
    empty_value_display = "-пусто-"


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "author", "favorites")
    search_fields = ("name", "author__username")
    list_filter = ("tags",)
    inlines = (IngredientInline, TagInline)
    empty_value_display = "-пусто-"

    def favorites(self, obj):
        return Favorites.objects.filter(recipe=obj).count()


class FavoritesAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = ("user__username", "user__email")
    empty_value_display = "-пусто-"


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = ("user__username", "user__email")
    empty_value_display = "-пусто-"


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorites, FavoritesAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
