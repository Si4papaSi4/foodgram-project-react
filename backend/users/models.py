from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from backend.constants import USER_EMAIL_MAX_LENGTH, USER_NAMES_MAX_LENGTH


class CustomUser(AbstractUser):
    first_name = models.CharField(
        max_length=USER_NAMES_MAX_LENGTH,
        blank=False,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=USER_NAMES_MAX_LENGTH,
        blank=False,
        verbose_name='Фамилия'
    )
    email = models.EmailField(
        max_length=USER_EMAIL_MAX_LENGTH,
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    subscriptions = models.ManyToManyField(
        'self',
        related_name='subscription',
        blank=True,
        symmetrical=False,
        verbose_name='Подписки'
    )

    REQUIRED_FIELDS = ["first_name", "last_name", "username"]
    USERNAME_FIELD = 'email'

    class Meta:

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def clean(self):
        super().clean()
        if self.username == 'me':
            raise ValidationError(
                'Нельзя использовать "me" в качестве username'
            )
