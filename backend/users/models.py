from django.db import models
from django.contrib.auth.models import AbstractUser
from users.constaints import (
    USER_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    VALIDATOR_REGEX
)


class User(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        unique=True,
        max_length=USER_MAX_LENGTH,
        verbose_name='Никнейм пользователя',
        validators=[VALIDATOR_REGEX,]
    )

    last_name = models.CharField(
        max_length=USER_MAX_LENGTH,
        verbose_name='Имя',
        null=True,
    )

    first_name = models.CharField(
        max_length=USER_MAX_LENGTH,
        verbose_name='Фамилия',
        null=True,
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
    )
    password = models.CharField(
        max_length=USER_MAX_LENGTH,
    )
    REQUIRED_FIELDS = ('id', 'first_name', 'last_name', 'email')

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
