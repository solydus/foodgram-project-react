from rest_framework.pagination import PageNumberPagination


class PageNumPagination(PageNumberPagination):
    """ количество объектов на странице. """
    page_size_query_param = 'limit'
