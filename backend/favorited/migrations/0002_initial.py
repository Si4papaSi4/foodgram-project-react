# Generated by Django 5.0.3 on 2024-04-02 10:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('favorited', '0001_initial'),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='favorite',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe', verbose_name='Рецепт'),
        ),
    ]