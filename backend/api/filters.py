import django_filters
from django_filters.rest_framework import FilterSet

from foodgram.models import Ingredient, Recipe, Tag


class IngredientNameFilter(FilterSet):
    """Фильтрация по началу названия."""
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Фильтрация по тегам, избранному и автору."""
    author = django_filters.CharFilter(
        field_name='author__id',
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = django_filters.CharFilter(method='get_favorite')
    is_in_shopping_cart = django_filters.CharFilter(
        method='filter_queryset_cart')

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def filter_queryset(self, queryset):
        request = self.request
        tags = request.query_params.get('tags')
        if tags:
            queryset = queryset.filter(tags__slug=tags)
        author = request.query_params.get('author')
        if author and request.user.is_authenticated:
            queryset = queryset.filter(author_id=author)
        is_in_shopping_cart = request.query_params.get('is_in_shopping_cart')
        if is_in_shopping_cart == '1' and request.user.is_authenticated:
            return queryset.filter(shopping_list__author=request.user)
        is_favorited = request.query_params.get('is_favorited')
        if is_favorited == '1' and request.user.is_authenticated:
            return queryset.filter(favorites__author=request.user)
        return queryset
