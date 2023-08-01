from rest_framework.pagination import PageNumberPagination


class ViewLevelPagination(PageNumberPagination):
    """Пагинация на уровне вьюсета."""

    page_size = 6
    page_size_query_param = "limit"
