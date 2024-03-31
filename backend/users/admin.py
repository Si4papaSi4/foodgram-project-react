from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
    )
    list_filter = ('email', 'username')
    list_display_links = ('email',)


admin.site.register(User, UserAdmin)
