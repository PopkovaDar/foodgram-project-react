from django.contrib import admin

from foodgram.models import Favorites, Ingredient, Recipe, ShoppingList, Tag
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Управление пользователем со страницы админа."""
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('username',)


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


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    """Управление пользователем со страницы админа."""
    list_display = (
        'author',
        'recipe',
    )
    search_fields = ('author',)
