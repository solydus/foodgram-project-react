from django.core.exceptions import ValidationError


def validate_ingredients(ingredients, ingredient_model):
    """
    Проверяет список ингредиентов на наличие дубликатов и правильность заполнения.
    :param ingredients: список словарей, содержащих данные об ингредиентах.
    :param ingredient_model: модель ингредиента, используемая в приложении.
    """
    unique_ids = set()
    for ingredient in ingredients:
        if not ingredient.get('id'):
            raise ValidationError('Не указан id ингредиента')
        ingredient_id = ingredient['id']
        if ingredient_id in unique_ids:
            raise ValidationError(f'{ingredient_id} - дублирующийся ингредиент')
        unique_ids.add(ingredient_id)

        try:
            ingredient_model.objects.get(id=ingredient_id)
        except ingredient_model.DoesNotExist:
            raise ValidationError(f'{ingredient_id} - ингредиент с таким id не найден')

        amount = ingredient.get('amount')
        if not isinstance(amount, int) or amount <= 0:
            raise ValidationError(f'Количество "{amount}" должно быть целым числом больше 0')


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
    if not isinstance(color, str) or not color.startswith('#') or len(color) != 7:
        raise ValidationError('Недопустимое значение цвета')


def validate_username(username):
    """
    Проверяет корректность имени пользователя.
    :param username: имя пользователя.
    """
    if not isinstance(username, str):
        raise ValidationError('Имя пользователя должно быть строкой')
    if username.lower() == 'me':
        raise ValidationError('Имя пользователя не может быть "me"')


def validate_real_name(name):
    """
    Проверяет корректность имени и фамилии пользователя.
    :param name: имя или фамилия пользователя.
    """
    if not isinstance(name, str):
        raise ValidationError('Имя и фамилия пользователя должны быть строкой')
    if len(name.strip()) == 0:
        raise ValidationError('Имя и фамилия пользователя не могут быть пустыми')