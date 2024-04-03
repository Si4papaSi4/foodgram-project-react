from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=128,
        blank=False,
        unique=True,
        verbose_name='Теги'
    )
    color = ColorField(
        default='#FF0000',
        blank=False,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=128,
        blank=False,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128,
        blank=False,
        unique=True,
        verbose_name='Ингредиент'
    )
    measurement_unit = models.CharField(
        blank=False,
        max_length=128,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class IngredientDetail(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        related_name='recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Ингредиент'
    )
    amount = models.IntegerField(
        validators=(MinValueValidator(1),),
        verbose_name='Количество'
    )

    class Meta:
        unique_together = ('recipe', 'ingredient')


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название',
    )
    image = models.ImageField(
        blank=False,
        verbose_name='Фотография'
    )
    text = models.TextField(
        blank=False,
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through=IngredientDetail,
        blank=False,
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=False,
        verbose_name='Теги'
    )
    cooking_time = models.IntegerField(
        blank=False,
        validators=(
            MinValueValidator(
                1,
                message='Минимальное время приготовления 1 минута'
            ),
        ),
        verbose_name='Время приготовления'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)
        unique_together = ('name', 'author', 'text')

    def __str__(self):
        return self.name
