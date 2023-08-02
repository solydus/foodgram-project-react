import re

from django.core.exceptions import ValidationError


def validate_ingredients(ingredients_list, val_model):
    """
    Проверяет список ингредиентов на наличие дубликатов и  заполнение.
    :param ingredients: список словарей, содержащих данные в ингредиентах.
    :param ingredient_model: модель ингредиента, используемая в приложении.
    """
    if len(ingredients_list) < 1:
        raise ValidationError(
            'Блюдо должно содержать хотя бы 1 ингредиент')
    unique_list = []
    for ingredient in ingredients_list:
        if not ingredient.get('id'):
            raise ValidationError('Укажите id ингредиента')
        ingredient_id = ingredient.get('id')
        if not val_model.objects.filter(pk=ingredient_id).exists():
            raise ValidationError(
                f'{ingredient_id}- ингредиент с таким id не найден')
        if id in unique_list:
            raise ValidationError(
                f'{ingredient_id}- дублирующийся ингредиент')
        unique_list.append(ingredient_id)
        ingredient_amount = ingredient.get('amount')
        if int(ingredient_amount) < 1:
            raise ValidationError(
                f'Количество {ingredient} должно быть больше 1')


def validate_tags(tags_list, val_model):
    """
    Проверяет корректность указанного времени приготовления.
    :param cooking_time: время приготовления в минутах.
    """
    for tag in tags_list:
        if not val_model.objects.filter(pk=tag).exists():
            raise ValidationError(f'{tag} - Такого тэга нет')


def validate_cooking_time(value):
    """
    Метод проверяет корректно ли указанное времени приготовления.
    Если нет - выбрасывает ValidationError.
    """
    if not value or int(value) < 1:
        raise ValidationError({
            'cooking_time': 'Укажите время приготовления'})


def validate_ingredient_name(value):
    """
    Проверяет корректность названия ингредиента.
    :param name: название ингредиента.
    """
    reg = r'^[\w%,"\'«»&()]+\Z'
    listik = value.split()
    for item in listik:
        if not re.fullmatch(reg, item):
            raise ValidationError({
                'Недопустимое значение имени {item}'})


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
