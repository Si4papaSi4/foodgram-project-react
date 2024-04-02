from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from favorited.admin import FavoriteInlineAdmin, ShoppingCartInlineAdmin

User = get_user_model()

admin.site.unregister(Group)


class UserAdmin(BaseUserAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
    )
    list_filter = ('email', 'username')
    inlines = (ShoppingCartInlineAdmin, FavoriteInlineAdmin)
    list_display_links = ('email',)


admin.site.register(User, UserAdmin)
