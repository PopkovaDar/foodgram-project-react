from django.contrib import admin

from foodgram.models import Favorite, Ingredient, Recipe, ShoppingList, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Управление тегами со страницы админа."""
    list_display = (
        'name',
        'slug',
        'color'
    )
    list_editable = ('slug',)
    search_fields = ('name', 'slug', 'color')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Управление ингредиентами со страницы админа."""

    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Управление рецептами со страницы админа."""

    list_display = (
        'id',
        'name',
        'image',
        'cooking_time',
    )
    list_editable = ('name',)
    search_fields = ('name',)


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Управление пользователем со страницы админа."""
    list_display = (
        'author',
        'recipe',
    )
    search_fields = ('author',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Управление пользователем со страницы админа."""
    list_display = (
        'author',
        'recipe',
    )
    search_fields = ('author',)
