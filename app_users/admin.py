from django.contrib import admin
from app_users.models import AppUser
from django.contrib.auth.admin import UserAdmin


class CustomAppUser(UserAdmin):
    # Specify the fields to display in the admin list view
    list_display = (
        "email",
        "mobile",
        "first_name",
        "last_name",
        "is_staff",
        "date_joined",
    )
    # Specify the fields to filter by in the admin list view
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    # Specify the fieldsets for the add and change forms
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "mobile")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )
    # Specify the add form fields
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "mobile",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
    # Specify the search fields for the admin search bar
    search_fields = ("email", "first_name", "last_name", "mobile")
    # Specify the ordering of objects in the admin list view
    ordering = ("email",)


# Register your models here.
admin.site.register(AppUser)
