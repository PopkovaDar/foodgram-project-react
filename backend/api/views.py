from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientNameFilter, RecipeFilter
from api.pagination import Pagination
from api.permissions import IsAuthorAdminOrReadOnly
from api.serializers import (FollowSerializer, FollowUserSerializer,
                             IngredientSerializer, RecipeFavoriteSerializer,
                             RecipeGetSerializer, RecipePostSerializer,
                             ShoppingListSerializer, TagSerializer,
                             UserSerializer)
from foodgram.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                             ShoppingList, Tag)
from users.models import FollowUser, User


class UserViewSet(UserViewSet):
    """Создание пользователей."""
    pagination_class = Pagination

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        url_path='me',
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        """Текущий пользователь."""
        serializer = UserSerializer(request.user, context={'request': request})
        if request.method == 'GET':
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated, ],)
    def subscribe(self, request, id):
        """Подписка или отписка от автора."""
        author = get_object_or_404(User, id=id)
        user = request.user
        data = {'author': author.id,
                'user': user.id}
        if request.method == 'POST':
            serializer = FollowSerializer(data=data,
                                          context={'request': request,
                                                   'pk': id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = FollowUser.objects.filter(
            author=author.id,
            user=user.id)
        if not subscription.exists():
            return Response({'errors': "Подписка не найдена!"},
                            status=status.HTTP_400_BAD_REQUEST)
        if subscription.exists():
            subscription.delete()
            return Response(
                subscription,
                status=status.HTTP_204_NO_CONTENT
            )
        return Response({'errors': "Вы не подписаны на данного автора!"},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        """Подписки пользователя."""
        paginate_queryset = self.paginate_queryset(
            FollowUser.objects.filter(user=request.user)
        )
        serializer = FollowUserSerializer(
            paginate_queryset,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


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
    pagination_class = Pagination
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

    def post_delete(self, serializer_class, models, request, pk):
        user = request.user
        data = {'author': user.id,
                'recipe': pk}
        if request.method == 'POST':
            serializer = serializer_class(
                data=data,
                context={'request': request, 'pk': pk}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        delete_follow = models.objects.filter(
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
        permission_classes=[IsAuthenticated, ],
        serializer_class=RecipeFavoriteSerializer,
        queryset=Favorite.objects.all(),
    )
    def favorite(self, request, pk):
        """Добавление и удаление из Избранного."""
        models = Favorite
        return self.post_delete(RecipeFavoriteSerializer, models, request, pk)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated, ],)
    def shopping_cart(self, request, pk):
        """Добавление и удаление из Списка покупок."""
        models = ShoppingList
        return self.post_delete(ShoppingListSerializer, models, request, pk)

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
        ).annotate(sum_amount=Sum('amount'))
        text = 'Что купить: \n'
        for ingredient in ingredients_list:
            text += (f' - {ingredient["ingredient__name"]}: '
                     f'{ingredient["sum_amount"]} '
                     f'{ingredient["ingredient__measurement_unit"]}.\n')
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment;filename="shopping_list.txt"'
        )
        return response
