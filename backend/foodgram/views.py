from users.models import User
from rest_framework import permissions, status, viewsets
from foodgram.models import Tag, Ingredient, Recipe
from foodgram.serializers import UserSerializer, TagSerializer, IngredientSerializer, RecipeSerializer, UserRegisterSerializer, UserSerializer
from foodgram.permissions import IsAuthorAdminOrReadOnly
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import AccessToken


class UserViewSet(viewsets.ViewSet):
    """Вьюсет для создания объектов модели жанров."""
    queryset = User.objects.all()
    http_method_names = ['post', 'get']
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания объектов модели жанров."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания объектов модели жанров."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания объектов модели жанров."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class AuthUserViewSet(UserViewSet):
    """Создание профиля."""

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    http_method_names = ['post']
    permission_classes = (AllowAny,)

