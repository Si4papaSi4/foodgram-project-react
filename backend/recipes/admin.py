from django import forms
from django.contrib import admin

from favorited.models import Favorite

from .models import Ingredient, Recipe, Tag

admin.site.empty_value_display = 'Не задано'


class IngredientsInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        if not any(form.cleaned_data for form in self.forms):
            raise forms.ValidationError('Должен быть хотя бы один ингредиент')


class IngredientsInlineAdmin(admin.TabularInline):
    model = Recipe.ingredients.through
    formset = IngredientsInlineFormset


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'added_in_favorite'
    )
    list_filter = ('author', 'name', 'tags')
    list_display_links = ('name', 'author',)
    inlines = (IngredientsInlineAdmin,)
    filter_horizontal = ('tags',)

    def added_in_favorite(self, obj):
        count = Favorite.objects.filter(recipe=obj).count()
        return count

    added_in_favorite.short_description = 'В избранном'


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)
    list_display_links = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
