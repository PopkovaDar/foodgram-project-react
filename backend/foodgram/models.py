from django.db import models
from users.models import User
from django.core.validators import RegexValidator

from users.constaints import (
    TAG_INGREDIENT_MAX_LENGTH,
    TAG_MAX_LENGTH_HEX,
)


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        max_length=TAG_INGREDIENT_MAX_LENGTH,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=TAG_INGREDIENT_MAX_LENGTH,
        verbose_name='Единицы изменения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(
        max_length=TAG_INGREDIENT_MAX_LENGTH,
        verbose_name='Название',
    )
    color = models.CharField(
        max_length=TAG_MAX_LENGTH_HEX,
        verbose_name='Цветовой код',
        validators=[RegexValidator(regex=r'^#[0-9A-Fa-f]{6}$')],
    )
    slug = models.SlugField(
        max_length=TAG_INGREDIENT_MAX_LENGTH,
        verbose_name='slug',
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )
    name = models.CharField(
        max_length=TAG_INGREDIENT_MAX_LENGTH,
        verbose_name='Название',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        upload_to='recipes_images'
    )
    cooking_time = models.PositiveIntegerField(
        default=1,
        verbose_name='Время приготовления(в минутах)',
    )
    is_favorited = models.BooleanField(
        default=True,
        verbose_name='Рецепт в избранном',
    )
    is_in_shopping_cart = models.BooleanField(
        default=True,
        verbose_name='Рецепт в корзине',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)


class TagRecipe(models.Model):
    """Модель тегов рецепта."""
    tags = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег',
        related_name='tagrecipe',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='tagrecipe'
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Тег рецепта'
        ordering = ('tags',)


class IngredientRecipe(models.Model):
    """Модель byuhtllbtynjd рецепта."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='recipes'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты',
        related_name='ingredient_recipe',
        default=None,
    )
    amount = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество ингредиента',
    )

    class Meta:
        verbose_name = 'Интгредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'


class ShoppingList(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopppinglist'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='shopppinglist'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'


class Favorites(models.Model):
    """Модель избранного."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='favorites'
    )

    class Meta:
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('user',)
