import re
from django.core.exceptions import ValidationError


def validate_ingredients(ingredients, ingredient_model):
    """
    Проверяет список ингредиентов на наличие дубликатов и  заполнение.
    :param ingredients: список словарей, содержащих данные в ингредиентах.
    :param ingredient_model: модель ингредиента, используемая в приложении.
    """
    unique_ids = set()
    for ingredient in ingredients:
        if not ingredient.get('id'):
            raise ValidationError('Не указан id ингредиента')
        ingredient_id = ingredient['id']
        if ingredient_id in unique_ids:
            raise ValidationError(f'{ingredient_id} - дубль ингредиента')
        unique_ids.add(ingredient_id)

        try:
            ingredient_model.objects.get(id=ingredient_id)
        except ingredient_model.DoesNotExist:
            raise ValidationError(f'{ingredient_id} - инг c id не найден')

        amount = ingredient.get('amount')
        if not isinstance(amount, int) or amount <= 0:
            raise ValidationError(f'Количество "{amount}" целое числом > 0')


def validate_tags(tags, tag_model):
    """
    Проверяет список тегов на существование в базе данных.
    :param tags: список тегов.
    :param tag_model: модель тега, используемая в приложении.
    """
    for tag in tags:
        if not tag_model.objects.filter(name=tag).exists():
            raise ValidationError(f'{tag} - такого тэга не существует')


def validate_cooking_time(cooking_time):
    """
    Проверяет корректность указанного времени приготовления.
    :param cooking_time: время приготовления в минутах.
    """
    if not isinstance(cooking_time, int) or cooking_time <= 0:
        raise ValidationError('Укажите корректное время приготовления')


def validate_ingredient_name(name):
    """
    Проверяет корректность названия ингредиента.
    :param name: название ингредиента.
    """
    if not isinstance(name, str):
        raise ValidationError('Название ингредиента должно быть строкой')
    if len(name.strip()) == 0:
        raise ValidationError('Название ингредиента не может быть пустым')


def validate_hex(color):
    """
    Проверяет корректность кода цвета.
    :param color: код цвета в формате HEX.
    """
    is_valid_type = isinstance(color, str)
    is_valid_start = color.startswith('#')
    is_valid_length = len(color) == 7

    if not is_valid_type or not is_valid_start or not is_valid_length:
        raise ValidationError('Недопустимое значение цвета')


def validate_real_name(value):
    """
    Валидатор для проверки корректности реального имени пользователя.
    """
    if not re.match(r'^[a-zA-Za-яА-ЯёЁ\s]+$', value):
        raise ValidationError(('Введите корректное имя.'))


def validate_username(value):
    """
    Валидатор для проверки корректности имени пользователя.
    """
    if not re.match(r'^[\w.@+-]+$', value):
        raise ValidationError(('Имя пможет содержать только буквы,цифры'))
