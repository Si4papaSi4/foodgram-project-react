# Generated by Django 5.0.3 on 2024-04-02 10:12

import colorfield.fields
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='Ингредиент')),
                ('measurement_unit', models.CharField(max_length=128, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('image', models.ImageField(upload_to='', verbose_name='Фотография')),
                ('text', models.TextField(verbose_name='Описание')),
                ('cooking_time', models.IntegerField(validators=[django.core.validators.MinValueValidator(1, message='Минимальное время приготовления 1 минута')], verbose_name='Время приготовления')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='Теги')),
                ('color', colorfield.fields.ColorField(default='#FF0000', image_field=None, max_length=25, samples=None, verbose_name='Цвет')),
                ('slug', models.SlugField(max_length=128, verbose_name='Слаг')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
        migrations.CreateModel(
            name='IngredientDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество')),
                ('ingredient', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='recipes.ingredient', verbose_name='Ингредиент')),
            ],
        ),
    ]
