from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constaints import EMAIL_MAX_LENGTH, USER_MAX_LENGTH, USERNAME_REGEX


class User(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        unique=True,
        max_length=USER_MAX_LENGTH,
        verbose_name='Никнейм пользователя',
        validators=[USERNAME_REGEX, ]
    )
    last_name = models.CharField(
        max_length=USER_MAX_LENGTH,
        verbose_name='Имя',
    )
    first_name = models.CharField(
        max_length=USER_MAX_LENGTH,
        verbose_name='Фамилия',
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
    )
    password = models.CharField(
        max_length=USER_MAX_LENGTH,
    )
    REQUIRED_FIELDS = ('first_name', 'last_name', 'email')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class FollowUser(models.Model):
    """Модель подписок."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',)

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='creator',
        verbose_name='Автор',)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('author',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribe_user'
            )
        ]
