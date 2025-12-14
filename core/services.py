from .models import Owner, Car, Outlay, OutlayAmount, OutlayCategoryChoice, OutlayTypeChoice, CarStatusChoice
from django.db.models import F, Value, Case, When, CharField
from django.db.models.functions import Concat
from .forms import OutlayFrom
from django.db import transaction


def get_owners_choice() -> list[tuple]:
    owners = Owner.objects.annotate(
        full_name=Concat(F("first_name"), Value(" "), F("last_name"))
    ).values("uuid", "full_name")

    return [(o["uuid"], o["full_name"]) for o in owners]

def get_cars_data(status: str = None) -> list[dict]:
   if status == None:
       status = CarStatusChoice.ACTIVE
   return list(Car.objects
        .filter(status=status)
        .values('mark', 'model', 'year', 'vin_code', 'status', 'license_plate')
    )

def get_car_param_to_view(car: Car) -> dict:
    return car.values('mark', 'model', 'year', 'vin_code', 'status', 'license_plate')

def create_outlay(
    type: str,
    description: str,
    cars: list[Car],
    price_per_item: float, 
    item_count: int,
    created_at,
    full_price: int = None,
    category: str = None,
    category_name: str = None,
    service_name: str = None,

    ) -> Outlay:
    if full_price:
        outlay_amout_obj: OutlayAmount = OutlayAmount.objects.create(
            full_price = full_price
        )
    else:
        outlay_amout_obj: OutlayAmount = OutlayAmount.objects.create(
            price_per_item = price_per_item,
            item_count = item_count
        )

    outlay_obj: Outlay = Outlay.objects.create(
        type = OutlayTypeChoice(type).label,
        category = OutlayCategoryChoice(category).label,
        category_name = category_name,
        service_name = service_name,
        description = description,
        amount = outlay_amout_obj,
        created_at = created_at
    )
    outlay_obj.cars.set(cars)

    return outlay_obj
    
def get_outlays() -> list[dict]:
    return Outlay.objects.select_related('outlay_cars', 'amount').values(
        'cars__mark', 'cars__model', 'cars__license_plate',
        'uuid', 'category', 'category_name', 'description', 'created_at', 'updated_at',
        'amount__price_per_item', 'amount__item_count', 'amount__full_price',
    )
    
def get_outlay_form_data(uuid):
    outlay: Outlay = Outlay.objects.get(uuid=uuid)
    amount: OutlayAmount = outlay.amount
    form = OutlayFrom(initial={
        'car': outlay.cars.all(),
        'service_type': outlay.type,
        'category': outlay.category,
        'category_name': outlay.category_name,
        'service_name': outlay.service_name,
        'description': outlay.description,
        'date': outlay.created_at if not outlay.updated_at else outlay.updated_at,
        'price_type': 'full' if amount.full_price else 'part',
        'full_price': amount.full_price,
        'price_per_item': amount.price_per_item,
        'item_count': amount.item_count,
    })
    return form

def get_outlay(uuid) -> Outlay:
    return Outlay.objects.get(uuid=uuid)

def update_outlay(uuid, form: OutlayFrom) -> Outlay:
    outlay = Outlay.objects.get(uuid = uuid)
    print(outlay)
    amount: OutlayAmount = outlay.amount

    cd = form.cleaned_data

    with transaction.atomic():
        outlay.type = cd["service_type"]
        outlay.category = cd.get("category")
        outlay.category_name = cd.get("category_name")
        outlay.service_name = cd.get("service_name")
        outlay.description = cd["description"]
        outlay.created_at = cd["date"]
        outlay.save()

        price_type = cd["price_type"]

        amount.full_price = None
        amount.price_per_item = None
        amount.item_count = None

        if price_type == "full":
            amount.full_price = cd["full_price"]
        else:
            amount.price_per_item = cd["price_per_item"]
            amount.item_count = cd["item_count"]

        amount.save()

        outlay.cars.set(cd["car"])

        outlay.save()

    return outlay