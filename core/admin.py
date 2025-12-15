from django.contrib import admin
from .models import User, Car, Owner
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class PersonAdmin(admin.ModelAdmin):
    list_display = ["username", "uuid", "role", "email", "is_email_verified"]


@admin.register(Car)
class PersonAdmin(admin.ModelAdmin):
    list_display = ["mark", "model", "year", "owner", "status"]


@admin.register(Owner)
class PersonAdmin(admin.ModelAdmin):
    list_display = ["uuid", "first_name", "last_name", "phone"]
