from django import forms
from .models import Car, Owner, FuelTypeChoice, StatusChoice, Service, CarPhoto
from .constants import label_vin
from .services import get_owners_choice


class MultipleFileInput(forms.FileInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs["multiple"] = True

    def value_from_datadict(self, data, files, name):
        if hasattr(files, "getlist"):
            return files.getlist(name)
        return files.get(name)


class AddCarForm(forms.ModelForm):
    # Поле photos виключено з форми, обробляється окремо в view
    # photos = forms.FileField(...)  # Видалено, обробляється вручну

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["owner"].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"

        self.fields["drive_type"].required = False

        if "photo" in self.fields:
            del self.fields["photo"]

        # Видалити поле photos з форми, воно обробляється окремо
        if "photos" in self.fields:
            del self.fields["photos"]

    owner = forms.ModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "border_input w-full"}),
        empty_label="Оберіть власника",
    )

    class Meta:
        model = Car
        fields = [
            "vin_code",
            "license_plate",
            "mark",
            "model",
            "year",
            "mileage",
            "color",
            "fuel_type",
            "status",
            "drive_type",
            "owner",
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
                attrs={"class": "border_input w-full", "placeholder": "Пробіг"}
            ),
            "color": forms.TextInput(
                attrs={"class": "border_input w-full", "placeholder": "Колір"}
            ),
            "fuel_type": forms.Select(attrs={"class": "border_input w-full"}),
            "status": forms.Select(attrs={"class": "border_input w-full"}),
            "drive_type": forms.TextInput(
                attrs={
                    "class": "border_input mark-model-input",
                    "placeholder": "Привід машини",
                }
            ),
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
            "first_name": forms.TextInput(
                attrs={"class": "border_input w-full", "placeholder": "Ім'я"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "border_input w-full", "placeholder": "Прізвище"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "border_input w-full", "placeholder": "+48..."}
            ),
            "telegram_link": forms.TextInput(
                attrs={"class": "border_input w-full", "placeholder": "@username"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "border_input w-full", "placeholder": "email@example.com"}
            ),
            "is_active_telegram": forms.CheckboxInput(attrs={"class": "h-4 w-4 text-blue-600"}),
        }


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["name", "location", "phone", "social_media", "has_social_media"]

        widgets = {
            "name": forms.TextInput(
                attrs={"class": "border_input w-full", "placeholder": "Назва сервісу"}
            ),
            "location": forms.TextInput(
                attrs={"class": "border_input w-full", "placeholder": "Адреса"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "border_input w-full", "placeholder": "+380..."}
            ),
            "social_media": forms.TextInput(
                attrs={
                    "class": "border_input w-full",
                    "placeholder": "Посилання на соціальні мережі",
                }
            ),
            "has_social_media": forms.CheckboxInput(attrs={"class": "h-4 w-4 text-blue-600"}),
        }
