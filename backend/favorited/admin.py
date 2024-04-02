from django.contrib import admin

from .models import Favorite, ShoppingCart


class FavoriteInlineAdmin(admin.TabularInline):
    model = Favorite


class ShoppingCartInlineAdmin(admin.TabularInline):
    model = ShoppingCart
