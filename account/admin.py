from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models


class AccountAdmin(UserAdmin):
    list_display = ('email', 'username', 'join_date', 'is_admin')
    search_fields = ('email', 'username')
    readonly_fields = ('id', 'join_date', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(models.Account, AccountAdmin)
# Register your models here.
