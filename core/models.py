from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password, **kwargs):
        if not email:
            raise ValueError('Provide Email filed')

        email = self.normalize_email(email=email)

        user = self.model(
            username=username,
            email=email,
            **kwargs
        )
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)

        return self.create_user(username, email, password, **kwargs)

class RolesChoice(models.TextChoices):
    CUSTOMER = "customer"
    ADMIN = "admin"
    MANAGER = "auto_manager"
    FINANCE= "finance_manager"

class AbstractTimeStampModel(models.Model):
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True


class User(AbstractBaseUser, AbstractTimeStampModel, PermissionsMixin):
    uuid = models.UUIDField(
        default=uuid.uuid4, 
        primary_key=True, 
        editable=False
    )
    phone=models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=RolesChoice.choices,
        default=RolesChoice.CUSTOMER
    )
    email = models.EmailField(blank=True, null=True, max_length=32, unique=True)
    username = models.CharField(max_length=32, unique=True)
    is_email_verified=models.BooleanField(default=False)
    is_blocked=models.BooleanField(default=False)
    last_login_at=models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()
    
    def save(self, *args, **kwargs):
        # custom logic
        super().save(*args, **kwargs)


    def __str__(self):
        return self.username
    

class Owner(AbstractTimeStampModel):
    uuid=models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    first_name=models.CharField(max_length=255)
    last_name=models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    telegram_link=models.CharField(max_length=255)
    email=models.CharField(max_length=55)
    is_active_telegram=models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class StatusChoice(models.TextChoices):
    ACTIVE = "Active"
    AWAITE = "Await"
    PROCESSING = "Processing"
    SERVICE = "Service"
    

class FuelTypeChoice(models.TextChoices):
    PETROL = "petrol", "Petrol"
    DIESEL = "diesel", "Diesel"
    ELECTRIC = "electric", "Electric"
    HYBRID = "hybrid", "Hybrid"
    

class Car(AbstractTimeStampModel):
    uuid=models.UUIDField(
        default=uuid.uuid4, 
        primary_key=True, 
        editable=False
    )
    mark=models.CharField(max_length=55)
    model=models.CharField(max_length=55)
    color=models.CharField(max_length=25)
    year=models.IntegerField()
    vin_code=models.CharField(max_length=55)
    license_plate = models.CharField(max_length=8)
    fuel_type = models.CharField(
        max_length=20,
        choices=FuelTypeChoice.choices,
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoice.choices,
        blank=True,
        null=True,
        default=StatusChoice.ACTIVE
    )
    mileage=models.DecimalField(max_digits=10, decimal_places=1)
    drive_type=models.CharField(max_length=55)
    photo = models.ImageField(upload_to="car_photos/", blank=True, null=True)
    
    owner=models.ForeignKey(
        Owner, 
        on_delete=models.CASCADE, 
        related_name="cars",
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.mark} {self.model} {self.year}"


class CarExpense(AbstractTimeStampModel):
    car = models.OneToOneField(
        Car,
        on_delete=models.CASCADE,
        related_name="expense"
    )
    @property
    def total_amount(self):
        service_total_amount=sum(
            [item.total for item in self.car.car_expenses.all()]
        )
        others_total_amount=sum(
            [item.total for item in self.car.other_expenses.all()]
        )
        return service_total_amount + others_total_amount


class Service(AbstractTimeStampModel):
    uuid=models.UUIDField(
        default=uuid.uuid4, 
        primary_key=True, 
        editable=False
    )
    name=models.CharField(max_length=55)
    phone=models.CharField(max_length=20, blank=True, null=True)
    location=models.CharField(max_length=255)
    social_media=models.CharField(max_length=55, blank=True)
    is_social_media=models.BooleanField(default=False)

    cars = models.ManyToManyField(
        Car,
        related_name="services"
    )  

    def __str__(self):
        return f"{self.name}"


class CarService(AbstractTimeStampModel):
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name="car_expenses"
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="car_services",
        null=True,
        blank=True
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
    uuid=models.UUIDField(
        default=uuid.uuid4, 
        primary_key=True, 
        editable=False
    )
    name=models.CharField(max_length=55)
    type=models.CharField(max_length=55)
    count=models.IntegerField()
    price_per_one=models.DecimalField(max_digits=10, decimal_places=2)

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name="other_expenses"
    )

    def total_amount(self):
        return self.count*self.price_per_one

    def __str__(self):
        return f"{self.name} {self.type} {self.count}"


class Comment(models.Model):
    invoice = models.ForeignKey(
        "Invoice",
        on_delete=models.CASCADE,
        related_name="comments"
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# TODO: implement proper Invoice → InvoiceItem → CarExpense structure

class Invoice(AbstractTimeStampModel):
    uuid=models.UUIDField(
        default=uuid.uuid4, 
        primary_key=True, 
        editable=False
    )
    name=models.CharField(max_length=55)
    file_path=models.CharField(max_length=255)
    invoice_data=models.JSONField(default=dict)
    invoice_amount=models.DecimalField(max_digits=10, decimal_places=2)
    is_archived=models.BooleanField(default=False)

    cars=models.ManyToManyField(
        Car, 
        related_name="invoices"
    )

    expense=models.ManyToManyField(
        CarExpense,
        related_name="expense_invoices"
    )
