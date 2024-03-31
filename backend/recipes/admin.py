# ice_cream/admin.py
from django.contrib import admin

from .models import Recipe, Ingredient, \
    Tag, Favorite  # , IngredientDetail, ShoppingCart

admin.site.empty_value_display = 'Не задано'


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'added_in_favorite'
    )
    list_filter = ('author', 'name', 'tags')
    list_display_links = ('name', 'author',)
    filter_horizontal = ('tags', 'ingredients')

    def added_in_favorite(self, obj):
        count = Favorite.objects.filter(recipe=obj).count()
        return count
    added_in_favorite.short_description = "В избранном"


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)
    list_display_links = ('name', )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
