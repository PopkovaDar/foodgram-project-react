import django.contrib.auth.password_validation as validators
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from foodgram.models import Recipe
from users.models import FollowUser, User


class UserRegisterSerializer(UserCreateSerializer):
    """Cоздание нового пользователя."""
    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'password'
        )

    @staticmethod
    def validate_password(password):
        validators.validate_password(password)
        return password


class UserRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор отображения списка рецептов."""
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'last_name',
            'first_name',
            'email',
        )


class FollowRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения списка авторов."""
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class UserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'username',
            'last_name',
            'first_name',
            'email',
            'is_subscribed'
        )
        model = User

    def get_is_subscribed(self, author):
        """отображение подписок."""
        request = self.context.get('request')
        if request.user.is_authenticated:
            return FollowUser.objects.filter(
                author=author,
                user=request.user,
            ).exists()
        return False


class FollowUserSerializer(serializers.ModelSerializer):
    """Сериализатор подписок пользователя."""
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FollowUser
        fields = (
            'id',
            'username',
            'last_name',
            'first_name',
            'email',
            'recipes',
            'recipes_count',
            'is_subscribed',
        )

    def get_is_subscribed(self, recipe):
        """Проверка наличия подписки."""
        author = recipe.author
        user = self.context.get('request').user
        return FollowUser.objects.filter(author=author, user=user).exists()

    def get_recipes(self, recipe):
        """Список рецептов автора."""
        author = recipe.author
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit', 6)
        limit = int(limit)
        return FollowRecipeSerializer(
            Recipe.objects.filter(author=author)[:limit],
            many=True
        ).data

    def get_recipes_count(self, recipe):
        """Количествво рецептов автора."""
        author = recipe.author
        return Recipe.objects.filter(author=author).count()


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор валидации подписок."""

    class Meta:
        model = FollowUser
        fields = (
            'id',
            'user',
            'author'
        )

    def validate(self, data):
        """Валидация на подписку."""
        author = data['author']
        user = data['user']
        if author == user:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя!')
        if FollowUser.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора!')
        return data

    def to_representation(self, author):
        """Данные о подписках."""
        serializer = FollowUserSerializer(author, context=self.context)
        return serializer.data
