from django.contrib import admin

from .models import Favorite, ShoppingCart


class FavoriteInlineAdmin(admin.TabularInline):
    model = Favorite


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    list_filter = ('user',)


class ShoppingCartInlineAdmin(admin.TabularInline):
    model = ShoppingCart


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    list_filter = ('user',)


admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
