from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    """Кастомная пагинация для Рецептов и Пользователей."""
    page_size_query_param = 'limit'
    page_size = 6
