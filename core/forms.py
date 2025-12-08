from django import forms
from .models import Car, Owner
from .constants import label_vin

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            "vin_code",
            "fuel_type",
            "mark",
            "model",
            "color",
            "year",
            "mileage",
            "drive_type",
            "photo",
            "owner",
        ]

        widgets = {
            "vin_code": forms.TextInput(attrs={
                "class": "border rounded w-full p-2",
                "placeholder": "VIN код"
            }),
            "fuel_type": forms.Select(attrs={
                "class": "border rounded w-full p-2"
            }),
            "mark": forms.TextInput(attrs={
                "class": "border rounded w-full p-2",
                "placeholder": "Марка"
            }),
            "model": forms.TextInput(attrs={
                "class": "border rounded w-full p-2",
                "placeholder": "Модель"
            }),
            "color": forms.TextInput(attrs={
                "class": "border rounded w-full p-2",
                "placeholder": "Колір"
            }),
            "year": forms.NumberInput(attrs={
                "class": "border rounded w-full p-2",
                "placeholder": "2020"
            }),
            "mileage": forms.NumberInput(attrs={
                "class": "border rounded w-full p-2",
                "placeholder": "123000"
            }),
            "drive_type": forms.TextInput(attrs={
                "class": "border rounded w-full p-2",
                "placeholder": "FWD / RWD / AWD"
            }),
            "photo": forms.ClearableFileInput(attrs={
                "class": "mt-2"
            }),
            "owner": forms.Select(attrs={
                "class": "border rounded w-full p-2 bg-white"
            }),
        }

class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = [
            "first_name",
            "last_name",
            "phone",
            "telegram_link",
            "email",
            "is_active_telegram",
        ]

        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "border rounded w-full p-2",
                "placeholder": "Ім'я"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "border rounded w-full p-2",
                "placeholder": "Прізвище"
            }),
            "phone": forms.TextInput(attrs={
                "class": "border rounded w-full p-2",
                "placeholder": "+380..."
            }),
            "telegram_link": forms.TextInput(attrs={
                "class": "border rounded w-full p-2",
                "placeholder": "@username"
            }),
            "email": forms.EmailInput(attrs={
                "class": "border rounded w-full p-2",
                "placeholder": "email@example.com"
            }),
            "is_active_telegram": forms.CheckboxInput(attrs={
                "class": "h-4 w-4 text-blue-600"
            }),
        }
