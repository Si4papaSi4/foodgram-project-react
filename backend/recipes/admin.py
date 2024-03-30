from django.contrib import admin

from .models import Ingredient, Recipe, Tag

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
