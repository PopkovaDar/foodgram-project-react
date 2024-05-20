from users.models import User
from rest_framework import viewsets
from foodgram.models import Tag, Ingredient, Recipe
from foodgram.serializers import TagSerializer, IngredientSerializer, RecipeGetSerializer, RecipePostSerializer, UserRegisterSerializer, UserSerializer, ShoppingListSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from foodgram.permissions import IsAuthorAdminOrReadOnly
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.decorators import action


class UserViewSet(viewsets.ViewSet):
    """Вьюсет для создания пользователей."""
    queryset = User.objects.all()
    http_method_names = ['post', 'get']
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        url_path='me',
        permission_classes=[IsAuthenticated],
    )
    def get_me(self, request):
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
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        """Определяет какой сериализатор будет использоваться"""
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipePostSerializer


class AuthUserViewSet(UserViewSet):
    """Создание профиля."""

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    http_method_names = ['post']
    permission_classes = (AllowAny,)


class ShoppingListViewSet(viewsets.ModelViewSet):
    """Список покупок."""

    queryset = Recipe.objects.all()
    serializer_class = ShoppingListSerializer
    http_method_names = ['post', 'get', 'delete']
    permission_classes = (AllowAny,)
