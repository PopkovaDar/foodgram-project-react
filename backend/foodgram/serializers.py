from rest_framework import serializers
from django.contrib.auth import get_user_model
from foodgram.models import Tag, Ingredient, Recipe, IngredientRecipe, ShoppingList, Favorites
from users.models import User, FollowUser
from djoser.serializers import UserSerializer,  UserCreateSerializer
import django.contrib.auth.password_validation as validators
from drf_extra_fields.fields import Base64ImageField
from django.shortcuts import get_object_or_404



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
        queryset=Ingredient.objects.all(),
        source='ingredient',
        write_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class IngredientAddRecipeSerializer(AddRecipeIngredientSerializer):
    """Сериализатор количества ингредиента для рецептов."""
    id = serializers.IntegerField()
    name = serializers.CharField(
        read_only=True)
    measurement_unit = serializers.CharField(
        read_only=True)
    amount = serializers.CharField(
        read_only=True)

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
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

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

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            author=request.user,
            recipe=obj
        ).exists()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorites.objects.filter(
            author=request.user,
            recipe=obj
        ).exists()


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
                  )

    def add_tags(self, tags, recipe):
        """Сохранение тегов рецепта."""
        recipe.tags.set(tags)

    def create_ingredients(self, ingredients, recipe):
        """Сохранение ингридиентов рецепта."""
        for ingredient_object in ingredients:
            ingredient = ingredient_object.get('ingredient')
            amount = ingredient_object.get('amount')
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

    def create(self, validated_data):
        """Создание рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        self.create_ingredients(ingredients, recipe)
        self.add_tags(tags, recipe)
        return recipe

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        serializers = RecipeGetSerializer(instance, context=context)
        return serializers.data

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.ingredient = validated_data.get('ingredients', instance.ingredients)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance


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


class RecipeFollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
            )


class FollowUserSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = FollowUser
        fields = ('id', 'username', 'last_name', 'first_name', 'email',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        """Подписан ли текущий пользователь на автора рецепта."""
        user = self.context.get('request').user
        return FollowUser.objects.filter(author=obj.author, user=user).exists()

    def get_recipes(self, obj):
        """Список рецептов автора."""
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit', 6)
        try:
            limit = int(limit)
        except ValueError:
            pass
        return RecipeFollowSerializer(
            Recipe.objects.filter(author=obj.author)[:limit],
            many=True
        ).data

    def get_recipes_count(self, obj):
        """Кол-во рецептов автора."""
        return Recipe.objects.filter(author=obj.author).count()


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели подписок."""

    class Meta:
        model = FollowUser
        fields = '__all__'

    def validate(self, data):
        """Валидация на подписку."""
        if data['author'] == data['user']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!')
        if FollowUser.objects.filter(author=data['author'], user=data['user']).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора!')
        return data

    def to_representation(self, author):
        return FollowUserSerializer(author, context=self.context).data


class ShoppingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingList
        fields = (
            'author',
            'recipe'
        )

    def to_representation(self, cart):
        recipe = cart.recipe
        serializers = RecipeFollowSerializer(recipe, context=self.context)
        return serializers.data

    def validate(self, data):
        user = data.get('author')
        recipe = data.get('recipe')
        if user.carts_list.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен!'
            )
        return data


class RecipeFavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorites
        fields = (
            'author',
            'recipe'
            )

    def to_representation(self, favorites):
        recipe = favorites.recipe
        serializers = RecipeFollowSerializer(recipe, context=self.context)
        return serializers.data

    def validate(self, data):
        user = data.get('author')
        recipe = data.get('recipe')
        if user.favorites_list.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен!'
            )
        return data
