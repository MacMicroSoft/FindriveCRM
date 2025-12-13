from django import forms
from .models import Car, Owner, FuelTypeChoice, StatusChoice, Service
from .constants import label_vin
from .services import get_owners_choice

class AddCarForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owner'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"

    owner = forms.ModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "border_input w-full"}),
        empty_label="Оберіть власника"
    )
    class Meta:
        model = Car
        fields = [
            'vin_code',
            'license_plate',
            'mark',
            'model',
            'year',
            'mileage',
            'color',
            'fuel_type',
            'status',
            'drive_type',
            'photo',
            'owner',
        ]

        widgets = {
            "vin_code": forms.TextInput(
                attrs={
                    "class": "border_input w-full",
                    "placeholder": "VIN код",
                }
            ),
            "license_plate": forms.TextInput(
                attrs={
                    "class": "border_input w-full",
                    "placeholder": "Номерний знак",
                }
            ),
            "mark": forms.TextInput(
                attrs={
                    "class": "border_input mark-model-input",
                    "placeholder": "Марка",
                }
            ),
            "model": forms.TextInput(
                attrs={
                    "class": "border_input mark-model-input",
                    "placeholder": "Модель",
                }
            ),
            "year": forms.NumberInput(
                attrs={
                    "class": "border_input w-full",
                    "placeholder": "Рік",
                }
            ),
            "mileage": forms.NumberInput(
                attrs={
                    "class": "border_input w-full",
                    "placeholder": "Пробіг"
                }
            ),
            "color": forms.TextInput(
                attrs={
                    "class": "border_input w-full",
                    "placeholder": "Колір"
                }
            ),
            "fuel_type": forms.Select(attrs={"class": "border_input w-full"}),
            "status": forms.Select(attrs={"class": "border_input w-full"}),
            "drive_type": forms.TextInput(
                attrs={
                    "class": "border_input mark-model-input",
                    "placeholder": "Привід машини",
                }
            ),
            "photo": forms.ClearableFileInput(attrs={
                "class": "border_input w-full",
                "accept": "image/*"
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

class ServiceForm(forms.ModelForm):
    class Meta:
        model=Service
        fields= [
            'name',
            'location',
            'phone',
            'social_media',
            'has_social_media'
        ]
