# ice_cream/admin.py
from django.contrib import admin

from .models import Recipe, Ingredient, \
    Tag  # , IngredientDetail, Favorite, ShoppingCart

admin.site.empty_value_display = 'Не задано'


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author'
    )
    list_editable = (
        'name',
        'author'
    )
    list_filter = ('author', 'name', 'tags')
    list_display_links = ('author',)
    filter_horizontal = ('tags', 'ingredients')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient)
