from django.contrib import admin

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
