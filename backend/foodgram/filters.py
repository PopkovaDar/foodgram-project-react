from rest_framework import filters
from foodgram.models import Ingredient
import django_filters


class FavoritedFilter(filters.BaseFilterBackend):
    """Фильтрация для страницы Избранного."""
    def filter_queryset(self, request, queryset, view):
        is_favorited = request.query_params.get('is_favorited')
        if is_favorited == '1':
            return queryset.filter(favorites__author=request.user)
        return queryset


class AuthorFilter(filters.BaseFilterBackend):
    """Фильтрация для страницы Избранного."""
    def filter_queryset(self, request, queryset, view):
        author = request.query_params.get('author')
        if author:
            queryset = queryset.filter(author_id=author)
        return queryset


class IngredientNameFilter(django_filters.FilterSet):
    """Фильтрация по началу названия."""
    name = django_filters.CharFilter(
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
