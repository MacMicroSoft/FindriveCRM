from django.contrib import admin
from .models import User, Car, Owner, Outlay, OutlayAmount, Chat, Message
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "uuid", "role", "email", "is_email_verified"]


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ["mark", "model", "year", "owner", "status"]


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ["uuid", "first_name", "last_name", "phone"]


@admin.register(Outlay)
class OutlayAdmin(admin.ModelAdmin):
    list_display = ["uuid", "type", "category", "description", "cars_list"]

    def cars_list(self, obj):
        return ", ".join(f"{car.mark} {car.model}" for car in obj.cars.all())

    cars_list.short_description = "Авто"


@admin.register(OutlayAmount)
class OutlayAmountAdmin(admin.ModelAdmin):
    list_display = ["uuid", "price_per_item", "item_count", "full_price"]


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ["uuid", "tg_chat_id", "user_first", "user_last", "tagname", "is_active"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["uuid", "chat", "sender", "sended"]
