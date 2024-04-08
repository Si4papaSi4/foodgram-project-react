from django import forms
from django.contrib import admin

from .models import Favorite, ShoppingCart


class FavoriteInlineAdmin(admin.TabularInline):
    model = Favorite


class FavoriteAdminForm(forms.ModelForm):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        recipe = cleaned_data.get('recipe')

        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise forms.ValidationError(
                "Такая комбинация значений уже существует.")

        return cleaned_data


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    list_filter = ('user',)
    form = FavoriteAdminForm


class ShoppingCartInlineAdmin(admin.TabularInline):
    model = ShoppingCart


class ShoppingCartAdminForm(forms.ModelForm):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        recipe = cleaned_data.get('recipe')

        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise forms.ValidationError(
                "Такая комбинация значений уже существует.")

        return cleaned_data


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    list_filter = ('user',)
    form = ShoppingCartAdminForm


admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
