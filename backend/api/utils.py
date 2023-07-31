from django.http import HttpResponse


def table_recipes(shopping_list):
    data = '\n'.join([' '.join(map(str, list(ing))) for ing in shopping_list])
    response = HttpResponse(data, content_type='text/txt')
    response['Content-Disposition'] = (
        f'attachment; filename={"shoping_list"}'
    )
    return response
