# Generated by Django 5.0.3 on 2024-04-07 12:48

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('favorited', '0004_alter_favorite_unique_together_and_more'),
        ('recipes', '0004_alter_ingredientdetail_ingredient'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='favorite',
            unique_together={('user', 'recipe')},
        ),
    ]