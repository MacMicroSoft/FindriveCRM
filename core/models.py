from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, password, **kwargs):
        if not email:
            raise ValueError("Provide Email filed")

        email = self.normalize_email(email=email)

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=email,
            **kwargs
        )
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, first_name, last_name, email, password, **kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_active", True)

        return self.create_user(first_name, last_name, email, password, **kwargs)


class UserRolesChoice(models.TextChoices):
    CUSTOMER = "customer"
    ADMIN = "admin"
    MANAGER = "auto_manager"
    FINANCE = "finance_manager"



class AbstractTimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    class Meta:
        abstract = True


class AbstractUserField(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    first_name = models.CharField(max_length=32, verbose_name="Імя")
    last_name = models.CharField(max_length=32, verbose_name="Призвіще")
    email = models.EmailField(max_length=64, unique=True, verbose_name="Пошта")
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Номер телефону")

    class Meta:
        abstract = True


class User(AbstractBaseUser, AbstractTimeStampModel, PermissionsMixin, AbstractUserField):
    role = models.CharField(
        max_length=20,
        choices=UserRolesChoice.choices,
        default=UserRolesChoice.CUSTOMER,
        verbose_name="Роль користувача"
    )
    is_email_verified = models.BooleanField(default=False, verbose_name="Верифікована пошта")
    last_login_at = models.DateTimeField(null=True, blank=True, verbose_name="В останнє залогінено")
    is_active = models.BooleanField(
        default=True, verbose_name="Активувати користувача",
        help_text="Дозволити користувачу вхід в обліковий запис. Якщо False користувач буде заблокований"
    )
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Owner(AbstractTimeStampModel, AbstractUserField):
    telegram_link=models.CharField(max_length=255, verbose_name="Посилання на телеграм")
    is_active_telegram=models.BooleanField(default=False, verbose_name="Активований телеграм")

    class Meta:
        ordering = ['last_name', 'first_name', '-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class CarStatusChoice(models.TextChoices):
    ACTIVE = "Active", "Активне авто"
    AWAIT = "Await", "Очікуюче авто"


class ServiceStatusChoice(models.TextChoices):
    """Статуси для сервісних подій (для фліт менеджера)"""
    UNKNOWN = "UNKNOWN", "Невідомо"
    NORMAL = "NORMAL", "В Нормі"
    IMPORTANT = "IMPORTANT", "Важливо"
    CRITICAL = "CRITICAL", "Критично"
    COMPLETED = "COMPLETED", "Виконано"


class CarFuelTypeChoice(models.TextChoices):
    PETROL = "petrol", "Бензин"
    DIESEL = "diesel", "Дизель"
    ELECTRIC = "electric", "Електричний"
    HYBRID = "hybrid", "Гібридний"

class CarDriveTypeChoice(models.TextChoices):
    FWD = "FWD", "Передній"
    RWD = "RWD", "Задній"
    AWD = "AWD", "Повний"


class Car(AbstractTimeStampModel):
    uuid = models.UUIDField(
        default=uuid.uuid4, 
        primary_key=True, 
        editable=False
    )
    mark = models.CharField(max_length=55, verbose_name="Марка авто")
    model = models.CharField(max_length=55, verbose_name="Модель авто")
    color = models.CharField(max_length=25, verbose_name="Колір авто")
    year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2050)], verbose_name="Рік випуску")
    vin_code = models.CharField(max_length=55, verbose_name="VIN номер авто", unique=True)
    license_plate = models.CharField(max_length=8, verbose_name="Номерний знак авто")
    fuel_type = models.CharField(
        max_length=20,
        choices=CarFuelTypeChoice.choices,
        blank=True,
        null=True,
        verbose_name="Тип пального"
    )
    status = models.CharField(
        max_length=20,
        choices=CarStatusChoice.choices,
        blank=True,
        null=True,
        default=CarStatusChoice.ACTIVE,
        verbose_name="Статус авто"
    )
    mileage = models.PositiveIntegerField(verbose_name="Пробіг авто")
    drive_type = models.CharField(
        max_length=55,
        choices=CarDriveTypeChoice.choices,
        blank=True,
        null=True,
        verbose_name="Привід авто"
    )
    photo = models.ImageField(upload_to="car_photos/", blank=True, null=True, verbose_name="Фото авто")
    
    owner = models.ForeignKey(
        Owner, 
        on_delete=models.CASCADE, 
        related_name="cars",
        null=True,
        blank=True,
        verbose_name="Власник авто"
    )

    @property
    def total_expenses_amount(self):
        service_total = sum(item.total for item in self.car_expenses.all())
        other_total = sum(item.total_amount() for item in self.other_expenses.all())
        return service_total + other_total

    def __str__(self):
        return f"{self.mark} {self.model} {self.year}"


class CarPhoto(AbstractTimeStampModel):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="photos")
    photo = models.ImageField(upload_to="car_photos/")
    order = models.IntegerField(default=0, help_text="Порядок відображення фото")

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"Photo for {self.car.mark} {self.car.model}"


class Service(AbstractTimeStampModel):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=55)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255)
    social_media = models.CharField(max_length=55, blank=True)
    has_social_media = models.BooleanField(default=False)

    cars = models.ManyToManyField(
        Car,
        related_name="services",
    )

    class Meta:
        ordering = ['name', '-created_at']

    def __str__(self):
        return f"{self.name}"


class CarService(AbstractTimeStampModel):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="car_expenses")

    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="car_services", null=True, blank=True
    )

    name = models.CharField(max_length=55)
    count = models.IntegerField()
    price_per_one = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total(self):
        return self.count * self.price_per_one

    def __str__(self):
        return f"{self.car} {self.name}"


class Other(AbstractTimeStampModel):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=55)
    type = models.CharField(max_length=55)
    count = models.IntegerField()
    price_per_one = models.DecimalField(max_digits=10, decimal_places=2)

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="other_expenses")

    def total_amount(self):
        return self.count * self.price_per_one

    def __str__(self):
        return f"{self.name} {self.type} {self.count}"


class Comment(models.Model):
    invoice = models.ForeignKey("Invoice", on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# TODO: implement proper Invoice → InvoiceItem → CarExpense structure

class OutlayTypeChoice(models.TextChoices):
    SERVICE = "service", "Сервіс"
    OTHER = "other", "Інші"


class OutlayCategoryChoice(models.TextChoices):
    FUEL = "fuel", "Паливо"
    PARTS = "parts", "Запчастини"
    DOCUMENTS = "documents", "Документи"
    ANOTHER = "another", "Інше"


class Outlay(AbstractTimeStampModel):
    uuid = models.UUIDField(
        default=uuid.uuid4, 
        primary_key=True, 
        editable=False
    )
    type = models.CharField(
        max_length=20,
        choices=OutlayTypeChoice.choices,
        default=OutlayTypeChoice.OTHER,
        verbose_name="Тип витрати",
    )
    category = models.CharField(
        max_length=20,
        choices=OutlayCategoryChoice.choices,
        default=None,
        verbose_name="Підкатегорія",
        null=True,
        blank=True
    )
    category_name = models.CharField(
        max_length=100,
        verbose_name="Власна підкатегорія",
        blank=True,
        null=True,
    )
    service_name = models.CharField(
        max_length=55,
        verbose_name="Назва сервісу",
        blank=True,
        null=True
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Назва витрати",
        help_text="Коротка назва витрати для швидкої ідентифікації (обов'язково для сервісу)",
        blank=True,
        null=True,
        default=""
    )
    comment = models.TextField(
        verbose_name="Коментар",
        blank=True,
        null=True,
        help_text="Додаткова інформація про витрату"
    )
    description = models.TextField(
        verbose_name="Опис",
        blank=True,
        null=True,
        help_text="Залишено для сумісності, використовуйте 'Назва витрати' та 'Коментар'"
    )
    amount = models.ForeignKey(
        "OutlayAmount",
        on_delete=models.PROTECT,
        db_column="amount_id",
    )

    cars = models.ManyToManyField(
        Car, 
        related_name="outlay_cars"
    )


class OutlayAmount(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4, 
        primary_key=True, 
        editable=False
    )
    price_per_item = models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Ціна за одиницю (PLN)", null=True, blank=True)
    item_count = models.PositiveSmallIntegerField(verbose_name="Кількість", null=True, blank=True)
    full_price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.full_price and self.item_count and self.price_per_item:
            self.full_price = self.item_count * self.price_per_item
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.uuid}"


class Invoice(AbstractTimeStampModel):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=55)
    file_path = models.CharField(max_length=255)
    invoice_data = models.JSONField(default=dict)
    invoice_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_archived = models.BooleanField(default=False)

    cars = models.ManyToManyField(Car, related_name="invoices")


class Notifications(AbstractTimeStampModel):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    message = models.TextField()
    message_type = models.CharField(max_length=55)
    send_at = models.DateTimeField()
    delivered_at = models.DateTimeField()

    is_sended = models.BooleanField(default=False)

class NotificationService(models.Model):
    """For sending and control service event status"""
    pass

class MillageHistory(models.Model):
    """Millage history for future metrics"""
    car=models.ForeignKey(Car, on_delete=models.CASCADE)
    millage=models.IntegerField()
    created_at=models.DateTimeField(auto_now=True)


class ServiceEventSchema(models.Model):
    """Schema for calc future car service"""
    schema_name=models.CharField(max_length=255)
    schema=models.JSONField()
    created_at=models.DateTimeField(auto_now=True)
    is_default=models.BooleanField(default=False)

class ServiceEvent(models.Model):
    """Model for monitoring service history"""
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=50)
    mileage_km = models.PositiveIntegerField()
    next_service_km = models.PositiveIntegerField()
    last_service_km = models.PositiveIntegerField()
    interval_km = models.PositiveIntegerField()
    date = models.DateField()
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

class CarServiceState(models.Model):
    """Save info about car service"""
    car = models.OneToOneField(Car, on_delete=models.CASCADE)
    service_plan = models.JSONField()
    mileage=models.PositiveBigIntegerField()
    updated_at = models.DateTimeField(auto_now=True)


class ServiceEventHistory(models.Model):
    """History of service events"""
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=50)
    mileage_km = models.PositiveIntegerField()
    date = models.DateField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    