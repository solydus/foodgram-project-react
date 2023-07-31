from django.db.models import Sum
from recipes.models import ShoppingCart, IngredientInRecipe


def generate_shopping_list(user):
    if not ShoppingCart.objects.filter(cart_owner=user).exists():
        return None

    rec_pk = ShoppingCart.objects.filter(
        cart_owner=user).values('recipe_id')
    ingredients = IngredientInRecipe.objects.filter(
        recipe_id__in=rec_pk).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
                amount=Sum('amount')).order_by()

    shopping_list = ''
    for item in ingredients:
        shopping_list += (f'{item["ingredient__name"]}: '
                          f'{item["amount"]} '
                          f'{item["ingredient__measurement_unit"]}\n')

    return shopping_list
