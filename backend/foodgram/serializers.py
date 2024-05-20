from rest_framework import serializers

from foodgram.models import Tag, Ingredient, Recipe, IngredientRecipe
from users.models import User, FollowUser
from djoser.serializers import UserSerializer,  UserCreateSerializer
import django.contrib.auth.password_validation as validators
from drf_extra_fields.fields import Base64ImageField


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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class UserRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор отображения авторов в рецептах."""
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'last_name',
            'first_name',
            'email',
            )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор отображения ингредиентов в рецептах."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class AddRecipeIngredientSerializer(serializers.ModelSerializer):
    """Вспомогательный cериалайзер для корректного добавления
       Ингредиентов в рецепт при его создании."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class IngredientAddRecipeSerializer(AddRecipeIngredientSerializer):
    """Сериализатор количества ингредиента для рецептов."""

    name = serializers.CharField(
        read_only=True,
        source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeGetSerializer(serializers.ModelSerializer):
    author = UserRecipeSerializer()
    ingredients = IngredientAddRecipeSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id',
                  'author',
                  'name',
                  'text',
                  'ingredients',
                  'tags',
                  'image',
                  'cooking_time',
                  'is_favorited',
                  'is_in_shopping_cart'
                  )


class RecipePostSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = AddRecipeIngredientSerializer(many=True)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image = Base64ImageField(use_url=True)

    class Meta:
        model = Recipe
        fields = ('id',
                  'author',
                  'name',
                  'text',
                  'ingredients',
                  'tags',
                  'image',
                  'cooking_time',
                  'is_favorited',
                  'is_in_shopping_cart'
                  )

    def add_tags(self, tags, recipe):
        """Сохранение в БД тэгов рецепта."""
        recipe.tags.set(tags)

    def create_ingredients(self, ingredients_data):
        ingredients_list = []
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            ingredient_amount = ingredient_data.get('amount')
            ingredient = Ingredient.objects.get(pk=ingredient_id)
            ingredient_recipe = IngredientRecipe.objects.create(ingredient=ingredient, amount=ingredient_amount)
            ingredients_list.append(ingredient_recipe)
        return ingredients_list

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags(tags, recipe)
        recipe.ingredients.add(*self.create_ingredients(ingredients_data))
        return recipe

    def to_representation(self, recipe):
        """Корректировка отображения информации о созданном рецепте."""
        return RecipeGetSerializer(recipe).data


class UserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        """Проверка наличия подписки."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return FollowUser.objects.filter(
            user=request.user,
            author=obj
        ).exists()

    class Meta:
        fields = (
            'id',
            'username',
            'last_name',
            'first_name',
            'email',
            'password',
            'is_subscribed'
        )
        model = User


class FollowUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUser
        fields = '__all__'


class ShoppingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'user', 'recipe')


class RecipeFollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
            )


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписки/отписки."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = FollowUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return FollowUser.objects.filter(user=user, author_id=obj.id).exists()
        return False

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.author).all()[:3]
        return RecipeFollowSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()
