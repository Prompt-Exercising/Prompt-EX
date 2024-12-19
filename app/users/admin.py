from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):  # type: ignore
    list_display = ["id", "email", "name", "is_active"]
