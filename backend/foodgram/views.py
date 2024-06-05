from users.models import User, FollowUser
from rest_framework import viewsets, mixins
from foodgram.models import Tag, Ingredient, Recipe, ShoppingList, Favorites, IngredientRecipe
from foodgram.serializers import TagSerializer, IngredientSerializer, FollowSerializer, RecipeFavoriteSerializer, FollowUserSerializer, RecipeGetSerializer, RecipePostSerializer, UserRegisterSerializer, UserSerializer, ShoppingListSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from foodgram.permissions import IsAuthorAdminOrReadOnly
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from foodgram.filters import FavoritedFilter, AuthorFilter, IngredientNameFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.http import HttpResponse
from foodgram.pagination import Pagination


class UserViewSet(UserViewSet):
    """Вьюсет для создания пользователей."""
    pagination_class = Pagination

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        url_path='me',
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
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
        author = get_object_or_404(User, id=id)
        data = {'author': author.id,
                'user': request.user.id}
        if request.method == 'POST':
            serializer = FollowSerializer(data=data,
                                          context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscription = FollowUser.objects.filter(
                author=author.id,
                user=request.user.id).delete()
            if subscription:
                return Response(status=status.HTTP_204_NO_CONTENT)
            if not subscription:
                return Response({'errors': "Подписка не найдена!"},
                                status=status.HTTP_404_NOT_FOUND)
            return Response({'errors': "Вы не подписаны на данного автора!"},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        queryset = FollowUser.objects.filter(user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowUserSerializer(
            pages,
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
    filterset_class = (IngredientNameFilter,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RecipePostSerializer
    filter_backends = [DjangoFilterBackend, FavoritedFilter, AuthorFilter,]
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
            queryset=Favorites.objects.all()
            )
    def favorite(self, request, pk):
        user = request.user
        data = {'author': user.id,
                'recipe': pk}
        if request.method == 'POST':
            serializer = RecipeFavoriteSerializer(data=data, context={'request': request, 'pk': pk})
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
                            status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated, ],)
    def shopping_cart(self, request, pk):
        user = request.user
        data = {'author': user.id,
                'recipe': pk}
        if request.method == 'POST':
            serializer = ShoppingListSerializer(data=data, context={'request': request, 'pk': pk})
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
                            status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated, ],)
    def download_shopping_cart(self, request):
        """Качаем список покупок."""
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_list__author=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        text = 'Что купить: \n\n'
        ingr_list = []
        for recipe in ingredients:
            ingr_list.append(recipe)
        for i in ingr_list:
            text += f'{i["ingredient__name"]}: {i["amount"]}, {i["ingredient__measurement_unit"]}.\n'
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="shopping_list.txt"')
        return response
