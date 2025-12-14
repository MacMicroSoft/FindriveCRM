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

    return outlay


import pdfplumber
import re 
import tabula
import pandas as pd


def pdf_parser(filepath) -> dict:
    TABLE_FIELDS = ('id', 'item_name', 'amount', 'price_netto', 'price_netto2', 'tax_percent', 'tax_price', 'price_brutto')

    tables = tables = tabula.read_pdf(filepath, pages="1", lattice=True)
    df = tables[0]
    df.columns = TABLE_FIELDS
    first_col = df.columns[0]
    df_filtered = df[pd.to_numeric(df[first_col], errors="coerce").notna()]
    table = df_filtered.to_dict(orient="records")


    reg_values = [
        ("invoice_number", re.compile(r'Faktura\s+numer\s+([A-Z\d/]+)', re.IGNORECASE)),
        ("sale_date", re.compile(r'Data\s+wystawienia:\s+Puchały,\s*(\d{4}-\d{2}-\d{2})', re.IGNORECASE)),
        ("sold_date_limit", re.compile(r'Data\s+sprzedaży:\s*(\d{4}-\d{2}-\d{2})', re.IGNORECASE)),
        ("payment_date_limit", re.compile(r'Termin\s+płatności:\s*(\d{4}-\d{2}-\d{2})', re.IGNORECASE)),
        ("payment", re.compile(r'Płatność:\s*([A-ZĄĆĘŁŃÓŚŻŹ]*)', re.IGNORECASE)),
        ("company_nip", re.compile(r'NIP\s+(\d+)', re.IGNORECASE)),
        ("company_bdo", re.compile(r'BDO\s+(\d+)', re.IGNORECASE)),
        ("price_netto", re.compile(r'Wartość netto\s+([\d,\s]*[\d,]*)\s+', re.IGNORECASE)),
        ("price_vat", re.compile(r'Wartość VAT\s+([\d,\s]*[\d,]*)\s+', re.IGNORECASE)),
        ("price_brutto", re.compile(r'Wartość brutto\s+([\d,\s]*[\d,]*)\s+', re.IGNORECASE)),
        ("to_pay", re.compile(r'Do zapłaty\s+([\d,\s]*[\d,]*)\s+', re.IGNORECASE)),
    ]

    str_data = {}

    with pdfplumber.open("test.pdf") as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            for line in text.split('\n'):
                for key, pattern in reg_values:
                    match = pattern.search(line)
                    if match: str_data[key] = match.group(1)
    

    return {
        'table': table,
        'str_data': str_data,
    }

