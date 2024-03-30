from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.fields import RegexValidator


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=150, blank=False, unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message="Никнейм должен содержать только буквы "
                        "(включая верхний и нижний регистр), цифры, "
                        "символы подчеркивания, точки, знаки '@', '+' или '-'."
            ),
        ]
    )
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    email = models.EmailField(max_length=254, unique=True, blank=False)
    subscriptions = models.ManyToManyField('self', related_name='subscription',
                                           blank=True, symmetrical=False)
    REQUIRED_FIELDS = ["first_name", "last_name", "username"]
    USERNAME_FIELD = 'email'
