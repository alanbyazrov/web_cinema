from users.models import User

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("phone", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Личные данные", {"fields": ("first_name", "last_name")}),
        ("Права доступа", {"fields": ("is_staff", "is_superuser")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone", "password1", "password2"),
            },
        ),
        ("Личные данные", {"fields": ("first_name", "last_name")}),
        ("Права доступа", {"fields": ("is_staff", "is_superuser")}),
    )
    search_fields = ("phone",)
    ordering = ("phone",)
    filter_horizontal = ()
    list_filter = ("is_staff", "is_superuser")
