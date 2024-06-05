from rest_framework import serializers
from foodgram.models import Tag, Ingredient, Recipe, IngredientRecipe, ShoppingList, Favorites
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


class PostIngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов в рецепт."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
        )
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'recipe', 'amount')


class GetIngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор количества ингредиента для чтения рецептов."""
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'amount',
            'measurement_unit',
        )


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор отображения рецептов при GET запросе."""
    author = UserRecipeSerializer()
    ingredients = GetIngredientRecipeSerializer(many=True, source='ingredient_recipe')
    tags = TagSerializer(many=True)
    image = Base64ImageField()
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

    def get_is_in_shopping_cart(self, shopping_cart):
        """Отображение рецепта в корзине."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return ShoppingList.objects.filter(
                author=user,
                recipe=shopping_cart
            ).exists()
        return False

    def get_is_favorited(self, favorites):
        """Отображение рецепта в избранном."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return Favorites.objects.filter(
                author=user,
                recipe=favorites
            ).exists()
        return False


class RecipePostSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов."""
    ingredients = PostIngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image = Base64ImageField(use_url=False)

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

    def validate(self, data):
        ingredients = data['ingredients']
        tags = data['tags']
        image = data['image']
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо добавить ингредиенты!'
            )
        ingredients_list = []
        for ingredient in ingredients:
            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть разными!'
                )
            ingredients_list.append(ingredient)
        if not tags:
            raise serializers.ValidationError(
                'Необходимо добавить тег!'
            )
        tag_list = []
        for tag in tags:
            if tag in tag_list:
                raise serializers.ValidationError(
                    'Теги должны быть разными!'
                )
            tag_list.append(tag)
        if not image:
            raise serializers.ValidationError(
                'Необходимо добавить изображение!'
            )
        return data

    def create_ingredients(self, recipe, ingredients):
        for ingredient_object in ingredients:
            ingredient = ingredient_object.get('ingredient')
            amount = ingredient_object.get('amount')
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

    def get_is_subscribed(self, author):
        """отображение подписок."""
        request = self.context.get('request')
        if request.user.is_authenticated:
            return FollowUser.objects.filter(
                author=author,
                user=request.user,
            ).exists()
        return False

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        validated_data['author'] = self.context.get('request').user
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, recipes, validated_data):
        """Обновление рецепта."""
        recipes.name = validated_data.get('name', recipes.name)
        recipes.text = validated_data.get('text', recipes.text)
        recipes.ingredient = validated_data.get('ingredients', recipes.ingredients)
        recipes.cooking_time = validated_data.get('cooking_time', recipes.cooking_time)
        recipes.image = validated_data.get('image', recipes.image)
        recipes.save()
        return recipes

    def to_representation(self, recipe):
        serializers = RecipeGetSerializer(recipe, context=self.context)
        return serializers.data


class RecipeFollowSerializer(serializers.ModelSerializer):
    """Сериализатор для корзины и избранного"""
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
            )


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
        return RecipeFollowSerializer(
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
        serializer = FollowUserSerializer(author, context=self.context)
        return serializer.data


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор Списка покупок."""
    class Meta:
        model = ShoppingList
        fields = (
            'author',
            'recipe'
        )

    def validate(self, data):
        user = data['author']
        recipe = data['recipe']
        if ShoppingList.objects.filter(author=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже был добавлен!'
            )
        return data

    def to_representation(self, shopping_list):
        recipe = shopping_list.recipe
        serializers = RecipeFollowSerializer(recipe, context=self.context)
        return serializers.data


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор Избранного."""

    class Meta:
        model = Favorites
        fields = (
            'author',
            'recipe'
            )

    def validate(self, data):
        user = data['author']
        recipe = data['recipe']
        if Favorites.objects.filter(author=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже был добавлен!'
            )
        return data

    def to_representation(self, favorites):
        recipe = favorites.recipe
        serializers = RecipeFollowSerializer(recipe, context=self.context)
        return serializers.data
