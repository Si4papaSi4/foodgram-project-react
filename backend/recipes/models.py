from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=128, blank=False, unique=True)
    color = ColorField(default='#FF0000', blank=False)
    slug = models.SlugField(max_length=128, blank=False)


class Ingredient(models.Model):
    name = models.CharField(max_length=128, blank=False, unique=True)
    measurement_unit = models.CharField(blank=False, max_length=128)


class IngredientDetail(models.Model):
    recipe = models.ForeignKey('Recipe',
                               related_name='recipe',
                               on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, null=True,
                                   on_delete=models.SET_NULL)
    amount = models.IntegerField(validators=(MinValueValidator(1),))

    class Meta:
        verbose_name_plural = 'Ingredient Details'
        unique_together = ('recipe', 'ingredient')


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=False)
    image = models.ImageField(blank=False)
    text = models.TextField(blank=False)
    ingredients = models.ManyToManyField(Ingredient,
                                         through=IngredientDetail,
                                         blank=False)
    tags = models.ManyToManyField(Tag, blank=False)
    cooking_time = models.IntegerField(blank=False,
                                       validators=(MinValueValidator(1),))

    class Meta:
        unique_together = ('name', 'author', 'text')


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'recipe')


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'recipe')
