from rest_framework import filters


class IsFavoritedFilter(filters.BaseFilterBackend):
    """Фильтрация для страницы Избранного."""
    def filter_queryset(self, request, queryset, view):
        is_favorited = request.query_params.get('is_favorited')
        if is_favorited is not None:
            if is_favorited == '1':
                return queryset.filter(favorites__author=request.user)
        return queryset
