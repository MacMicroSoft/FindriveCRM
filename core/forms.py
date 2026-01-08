from django import forms
from .models import (
    Car, 
    Owner, 
    OutlayCategoryChoice, 
    Service, 
    CarServiceState
)

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
            "drive_type": forms.Select(attrs={"class": "border_input w-full"}),
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
                attrs={"class": "border_input w-full", "placeholder": "+48123456789"}
            ),
            "telegram_link": forms.TextInput(
                attrs={"class": "border_input w-full", "placeholder": "@username"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "border_input w-full", "placeholder": "email@example.com"}
            ),
            "is_active_telegram": forms.CheckboxInput(attrs={"class": "h-4 w-4 text-blue-600"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_active_telegram'].required = False
        self.fields['telegram_link'].required = False
    
    def clean_phone(self):
        import re
        phone = self.cleaned_data.get('phone')
        
        if not phone or phone.strip() == '':
            return phone  # Поле не обов'язкове, якщо порожнє - повертаємо як є
        
        phone = phone.strip()
        
        # Видалити всі пробіли, дефіси та інші символи для перевірки
        phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Перевірити формат польського номера: +48XXXXXXXXX (9 цифр після +48)
        # Або 48XXXXXXXXX (без +)
        polish_phone_pattern = r'^(\+?48)(\d{9})$'
        
        match = re.match(polish_phone_pattern, phone_clean)
        if not match:
            raise forms.ValidationError(
                'Номер телефону повинен бути у польському форматі: +48XXXXXXXXX '
                '(9 цифр після +48). Наприклад: +48123456789'
            )
        
        # Повернути у стандартному форматі +48XXXXXXXXX
        formatted_phone = f"+48{match.group(2)}"
        
        # Перевірити довжину (якщо модель має max_length=10, це буде помилка)
        if len(formatted_phone) > 15:
            raise forms.ValidationError('Номер телефону занадто довгий')
        
        return formatted_phone


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


class OutlayFrom(forms.Form):
    car = forms.ModelChoiceField(
        queryset=Car.objects.all(),
        required=True,
        label='Автомобіль',
        widget=forms.Select(attrs={
            "class": "border_input w-full",
            "placeholder": "Оберіть автомобіль"
        })
    )
    service_type = forms.ChoiceField(
        required=True,
        label="Тип витрати",
        choices=[('other', 'Інші'), ('service', 'Сервіс')],
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
    name = forms.CharField(
        required=False,
        label='Назва витрати',
        max_length=255,
        widget=forms.TextInput(
            attrs={"placeholder": "Наприклад: Заправка палива, Ремонт гальм тощо"}
        )
    )
    comment = forms.CharField(
        required=False,
        label='Коментар',
        widget=forms.Textarea(attrs=
            {"placeholder": "Додаткова інформація про витрату (необов'язково)",
            "class": "border_input w-full",
            "rows": 3
        }),
    )
    description = forms.CharField(
        required=False,
        label='Опис (застаріле)',
        widget=forms.Textarea(attrs=
            {"placeholder": "Не використовуйте це поле",
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


class CarServiceForm(forms.ModelForm):
    regulation_name = forms.CharField(
        required=False,
        max_length=255,
        label='Назва регламенту',
        widget=forms.TextInput(
            attrs={
                "class": "border_input w-full",
                "placeholder": "Наприклад: SYNCHRONIZED SERVICE REGULATION (EVERY 10 000 KM)"
            }
        )
    )
    services_json = forms.CharField(
        required=False,
        label='Сервіси (JSON)',
        widget=forms.Textarea(
            attrs={
                "class": "border_input w-full",
                "rows": 10,
                "style": "display: none;"
            }
        )
    )
    
    class Meta:
        model = CarServiceState
        fields = ['car', 'service_plan', 'mileage']
        widgets = {
            'car': forms.Select(attrs={
                "class": "border_input w-full",
                "placeholder": "Оберіть автомобіль"
            }),
            'service_plan': forms.Textarea(attrs={
                "class": "border_input w-full",
                "rows": 10,
                "style": "display: none;"
            }),
            'mileage': forms.NumberInput(attrs={
                "class": "border_input w-full",
                "placeholder": "Пробіг автомобіля"
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Зробити service_plan необов'язковим, бо воно будується з services_json
        self.fields['service_plan'].required = False
    
    def clean_services_json(self):
        import json
        # Читаємо з data напряму, бо це поле не з моделі
        services_str = self.data.get('services_json', '')
        
        if not services_str or (isinstance(services_str, str) and services_str.strip() == ''):
            return None
        
        try:
            services = json.loads(services_str) if isinstance(services_str, str) else services_str
        except json.JSONDecodeError as e:
            raise forms.ValidationError(f"Невірний JSON формат: {str(e)}")
        
        if not isinstance(services, list):
            raise forms.ValidationError("Сервіси повинні бути масивом")
        
        if len(services) == 0:
            raise forms.ValidationError("Масив сервісів не може бути порожнім")
        
        required_fields = ['name', 'interval_km', 'last_service_km']
        
        for i, service in enumerate(services):
            if not isinstance(service, dict):
                raise forms.ValidationError(f"Сервіс {i+1} повинен бути об'єктом")
            
            # Генерувати key автоматично, якщо його немає
            if 'key' not in service or not service.get('key'):
                if 'name' in service and service.get('name'):
                    # Проста транслітерація для генерації key
                    name = service['name'].lower()
                    # Базова транслітерація українських літер
                    translit_map = {
                        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'ґ': 'g', 'д': 'd', 'е': 'e', 'є': 'ye',
                        'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'y', 'к': 'k', 'л': 'l',
                        'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
                        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ь': '', 'ю': 'yu',
                        'я': 'ya'
                    }
                    for ukr, eng in translit_map.items():
                        name = name.replace(ukr, eng)
                    # Замінити всі не-латинські символи на підкреслення
                    import re
                    key = re.sub(r'[^a-z0-9_]', '_', name)
                    key = re.sub(r'_+', '_', key).strip('_')
                    service['key'] = key if key else f'service_{i+1}'
                else:
                    service['key'] = f'service_{i+1}'
            
            for field in required_fields:
                if field not in service:
                    raise forms.ValidationError(f"Сервіс {i+1} не містить поле '{field}'")
            if not isinstance(service.get('interval_km'), (int, float)) or service.get('interval_km') <= 0:
                raise forms.ValidationError(f"Сервіс {i+1}: interval_km повинен бути додатнім числом")
            if not isinstance(service.get('last_service_km'), (int, float)) or service.get('last_service_km') < 0:
                raise forms.ValidationError(f"Сервіс {i+1}: last_service_km повинен бути невід'ємним числом")
            
            # Валідація статусу
            if 'status' in service:
                from .models import ServiceStatusChoice
                valid_statuses = [choice[0] for choice in ServiceStatusChoice.choices]
                if service['status'] not in valid_statuses:
                    raise forms.ValidationError(
                        f"Сервіс {i+1}: Невірний статус '{service['status']}'. Дозволені статуси: {', '.join(valid_statuses)}"
                    )
            
            # Валідація: останній сервіс не може бути більший за пробіг
            # (mileage буде перевірено в clean методі, де є доступ до нього)
        
        return services
    
    def clean(self):
        cleaned_data = super().clean()
        regulation_name = cleaned_data.get('regulation_name')
        services_json = cleaned_data.get('services_json')
        mileage = cleaned_data.get('mileage')
        
        # Якщо є services_json, будуємо service_plan
        if services_json is not None and len(services_json) > 0:
            if not mileage:
                raise forms.ValidationError({'mileage': 'Пробіг обов\'язковий при введенні сервісів'})
            if not regulation_name:
                raise forms.ValidationError({'regulation_name': 'Назва регламенту обов\'язкова при введенні сервісів'})
            
            # Додаткова валідація: останній сервіс не може бути більший за пробіг
            for i, service in enumerate(services_json):
                if not isinstance(service, dict):
                    continue
                last_service_km = service.get('last_service_km', 0)
                if mileage and last_service_km > mileage:
                    raise forms.ValidationError({
                        'services_json': f'Сервіс {i+1}: Останній сервіс ({last_service_km} км) не може бути більший за поточний пробіг ({mileage} км)'
                    })
            
            cleaned_data['service_plan'] = {
                "regulation_name": regulation_name,
                "current_mileage_km": mileage,
                "services": services_json
            }
        elif not cleaned_data.get('service_plan'):
            # Якщо немає ні service_plan, ні services_json - помилка
            raise forms.ValidationError({'services_json': 'Додайте хоча б один сервіс'})
        
        return cleaned_data