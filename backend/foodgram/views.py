from users.models import User, FollowUser
from rest_framework import viewsets, mixins
from foodgram.models import Tag, Ingredient, Recipe, ShoppingList, Favorites
from foodgram.serializers import TagSerializer, IngredientSerializer, FollowSerializer, RecipeFavoriteSerializer, FollowUserSerializer, RecipeGetSerializer, RecipePostSerializer, UserRegisterSerializer, UserSerializer, ShoppingListSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from foodgram.permissions import IsAuthorAdminOrReadOnly
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from djoser.views import UserViewSet


class Pagination(PageNumberPagination):
    """Кастомная пагинация для Рецептов и Пользователей."""
    page_size_query_param = 'limit'
    page_size = 6


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
        serializer = UserSerializer(request.user)
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
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        sudscriptions = FollowUser.objects.filter(user=request.user)
        pages = self.paginate_queryset(sudscriptions)
        serializer = FollowUserSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

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
            subscription, _ = FollowUser.objects.filter(
                author=author.id,
                user=request.user.id).delete()
            if subscription:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': "Вы не подписаны на этого автора!"},
                            status=status.HTTP_400_BAD_REQUEST)


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
    http_method_names = ['get', ]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RecipePostSerializer
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

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def favorites(self, request):
        user = request.user
        favorite_recipes = user.favorites_list.all()  # Получаем избранные рецепты для текущего пользователя
        serializer = RecipeGetSerializer(favorite_recipes, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

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


class AuthUserViewSet(UserViewSet):
    """Создание профиля."""

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    http_method_names = ['post']
    permission_classes = (AllowAny,)
