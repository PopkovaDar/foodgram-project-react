from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.constaints import (COLOR_VALIDATOR, TAG_INGREDIENT_MAX_LENGTH,
                              TAG_MAX_LENGTH_HEX)
from users.models import User


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        max_length=TAG_INGREDIENT_MAX_LENGTH,
        verbose_name='Название ингредиента',
        unique=True,
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
        validators=[COLOR_VALIDATOR, ]
    )
    slug = models.SlugField(
        max_length=TAG_INGREDIENT_MAX_LENGTH,
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
        upload_to='foodgram/'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления(в минутах)',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10000)]
    )
    created_at = models.DateTimeField(
        'Добавлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)


class IngredientRecipe(models.Model):
    """Модель ингредиентов рецепта."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты',
        related_name='recipe_ingredient'
    )
    amount = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество ингредиента',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10000)]
    )

    class Meta:
        verbose_name = 'Интгредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        default_related_name = 'ingredient_recipe'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_recipe'
            )
        ]


class ShoppingList(models.Model):
    """Модель списка покупок."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='shopping_list',
    )

    class Meta:
        ordering = ('author',)
        default_related_name = 'carts_list'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'],
                name='cart_author_recipe'
            )
        ]


class Favorite(models.Model):
    """Модель избранного."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='favorite'
    )

    class Meta:
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('author',)
        default_related_name = 'favorite_list'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'],
                name='favorite_author_recipe'
            )
        ]
