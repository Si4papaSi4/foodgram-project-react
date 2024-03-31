from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.fields import RegexValidator


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=150,
        blank=False,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message="Никнейм должен содержать только буквы "
                        "(включая верхний и нижний регистр), цифры, "
                        "символы подчеркивания, точки, знаки '@', '+' или '-'."
            ),
        ],
        verbose_name='Никнейм'
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Фамилия'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        verbose_name='Адрес электронной почты'
    )
    subscriptions = models.ManyToManyField(
        'self',
        related_name='subscription',
        blank=True,
        symmetrical=False,
        verbose_name='Подписчики'
    )
    REQUIRED_FIELDS = ["first_name", "last_name", "username"]
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
