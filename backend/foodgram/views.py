from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from foodgram.filters import IngredientNameFilter, RecipeFilter
from foodgram.models import (Favorites, Ingredient, IngredientRecipe, Recipe,
                             ShoppingList, Tag)
from foodgram.permissions import IsAuthorAdminOrReadOnly
from foodgram.serializers import (IngredientSerializer,
                                  RecipeFavoriteSerializer,
                                  RecipeGetSerializer, RecipePostSerializer,
                                  ShoppingListSerializer, TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для создания тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get', ]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для создания ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientNameFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorAdminOrReadOnly, IsAuthenticatedOrReadOnly]
    serializer_class = RecipePostSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        """Определяет какой сериализатор будет использоваться"""
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipePostSerializer

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated, ],
        serializer_class=RecipeFavoriteSerializer,
        queryset=Favorites.objects.all(),
    )
    def favorite(self, request, pk):
        """Добавление и удаление из Избранного."""
        user = request.user
        data = {'author': user.id,
                'recipe': pk}
        if request.method == 'POST':
            serializer = RecipeFavoriteSerializer(
                data=data,
                context={'request': request, 'pk': pk}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            delete_follow = Favorites.objects.filter(
                author=user,
                recipe__id=pk)
            if delete_follow.exists():
                delete_follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': "Рецепт не существует!"},
                            status=status.HTTP_404_NOT_FOUND)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated, ],)
    def shopping_cart(self, request, pk):
        """Добавление и удаление из Списка покупок."""
        user = request.user
        data = {'author': user.id,
                'recipe': pk}
        if request.method == 'POST':
            serializer = ShoppingListSerializer(
                data=data,
                context={'request': request, 'pk': pk}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            delete_follow = ShoppingList.objects.filter(
                author=user,
                recipe__id=pk)
            if delete_follow.exists():
                delete_follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': "Рецепт не существует!"},
                            status=status.HTTP_404_NOT_FOUND)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated, ],)
    def download_shopping_cart(self, request):
        """Качаем список покупок."""
        ingredients_list = IngredientRecipe.objects.filter(
            recipe__shopping_list__author=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        text = 'Что купить: \n'
        for ingredient in ingredients_list:
            text += (f' - {ingredient["ingredient__name"]}: '
                     f'{ingredient["amount"]} '
                     f'{ingredient["ingredient__measurement_unit"]}.\n')
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response
