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

    def save_model(self, request, obj, form, change):
        if not change:
            if Favorite.objects.filter(user=obj.user,
                                       recipe=obj.recipe).exists():
                raise ValueError("Такая комбинация значений уже существует.")
        super().save_model(request, obj, form, change)


class ShoppingCartInlineAdmin(admin.TabularInline):
    model = ShoppingCart


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    list_filter = ('user',)

    def save_model(self, request, obj, form, change):
        if not change:
            if ShoppingCart.objects.filter(user=obj.user,
                                           recipe=obj.recipe).exists():
                raise ValueError("Такая комбинация значений уже существует.")
        super().save_model(request, obj, form, change)


admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
