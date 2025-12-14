from django import forms
from .models import Car, Owner, Outlay, CarExpense, OutlayCategoryChoice, Service
from .constants import label_vin

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
            "drive_type": forms.Select(attrs={"class": "border_input w-full"}),
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


class OutlayFrom(forms.Form):
    car = forms.ModelMultipleChoiceField(
        queryset=Car.objects.all(),
        required=True,
        label='Автомобіль',
        widget=forms.SelectMultiple(attrs={
            "class": "border_input w-full",
            "placeholder": "Оберіть автомобіль"
        })
    )
    service_type = forms.ChoiceField(
        required=True,
        label="Тип витрати",
        choices=[('other', 'Other'), ('service', 'Service')],
        widget=forms.RadioSelect(attrs={"class": "service-radio"}),
        initial='other',
    )
    category = forms.ChoiceField(
        required=False,
        label='Підкатегорія',
        choices=OutlayCategoryChoice.choices,
        widget=forms.Select(attrs={"placeholder": "Оберіть категорію"})

    )
    category_name = forms.CharField(
        required=False,
        label='Власна підкатегорія',
        widget=forms.TextInput(
            attrs={"placeholder": "Введіть назву підкатегорії"}
        )
    )
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        required=False,
        label='Сервіс',
        widget=forms.Select(attrs={"placeholder": "Оберіть сервіс"})
    )
    service_name = forms.CharField(
        required=False,
        label='Введіть назву сервісу вручну',
        widget=forms.TextInput(
            attrs={"placeholder": "Введіть назву сервісу вручну"}
        )
    )
    description = forms.CharField(
        required=True,
        label='Опис',
        widget=forms.Textarea(attrs=
            {"placeholder": "Детальний опис витрати",
            "class": "border_input w-full"
        }),
    )
    date = forms.DateField(
        required=True,
        label='Дата',
        widget=forms.DateInput(format='%d/%m/%Y', attrs={"type": "date"})
    )
    price_type = forms.ChoiceField(
        required=True,
        label='Вартість (PLN)',
        choices=[('full', 'Загальна сума'), ('part', 'Ціна х Кількість')],
        widget=forms.RadioSelect(attrs={"class": "service-radio"}),
        initial='full'
    )
    full_price = forms.DecimalField(
        required=False,
        label='Загальна сума (PLN)',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(),
    )
    price_per_item = forms.DecimalField(
        required=False,
        label='Ціна за одиницю (PLN)',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(),
    )
    item_count = forms.IntegerField(
        required=False,
        label='Кількість',
        min_value=1,
        widget=forms.NumberInput(),
    )

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get("service")
        service_name = cleaned_data.get("service_name")

        if not service and not service_name and cleaned_data.get("service_type") == "service":
            self.add_error("service_name", "Введіть сервіс або оберіть зі списку.")
        
        price_type = cleaned_data.get("price_type")
        full_price = cleaned_data.get("full_price")
        price_per_item = cleaned_data.get("price_per_item")
        item_count = cleaned_data.get("item_count")

        if price_type == "full" and not full_price:
            self.add_error("full_price", "Заповніть загальну суму.")
        elif price_type == "part" and (not price_per_item or not item_count):
            self.add_error("price_per_item", "Заповніть ціну та кількість.")

        service_type = cleaned_data.get("service_type")
        category = cleaned_data.get("category")

        if service_type == "service" and not category:
            self.add_error("category", "Підкатегорія обов'язкова для сервісу.")