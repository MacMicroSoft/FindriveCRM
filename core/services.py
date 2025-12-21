from .models import Owner, Car, Outlay, OutlayAmount, OutlayCategoryChoice, OutlayTypeChoice, CarStatusChoice
from django.db.models import F, Value, Case, When, CharField
from django.db.models.functions import Concat
from .forms import OutlayFrom
from django.db import transaction
import pymupdf
from pathlib import Path
import re



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


class PDFCore:
    TABLE_FIELDS = ('id', 'item_name', 'amount', 'price_netto', 'price_netto2', 'tax_percent', 'tax_price', 'price_brutto')
    REG_FIELDS = [
        ("invoice_number", re.compile(r'Faktura\s+numer\s+([A-Z\d/]+)', re.IGNORECASE)),
        ("sale_date", re.compile(r'Data\s+wystawienia:\s+Puchały,\s*(\d{4}-\d{2}-\d{2})', re.IGNORECASE)),
        ("sold_date_limit", re.compile(r'Data\s+sprzedaży:\s*(\d{4}-\d{2}-\d{2})', re.IGNORECASE)),
        ("payment_date_limit", re.compile(r'Termin\s+płatności:\s*(\d{4}-\d{2}-\d{2})', re.IGNORECASE)),
        ("payment", re.compile(r'Płatność:\s*([A-ZĄĆĘŁŃÓŚŻŹ]*)', re.IGNORECASE)),
        [("company_nip", re.compile(r'NIP\s+(\d+)', re.IGNORECASE)),
        ("company_bdo", re.compile(r'BDO\s+(\d+)', re.IGNORECASE))],
        re.compile(r'^LP\n.*', re.IGNORECASE),
        ("price_netto", re.compile(r'Wartość netto\s+([\d,\s]*[\d,]*)\s+', re.IGNORECASE)),
        ("price_vat", re.compile(r'Wartość VAT\s+([\d,\s]*[\d,]*)\s+', re.IGNORECASE)),
        ("price_brutto", re.compile(r'Wartość brutto\s+([\d,\s]*[\d,]*)\s+', re.IGNORECASE)),
        ("to_pay", re.compile(r'Do zapłaty\s+([\d,\s]*[\d,]*)\s+', re.IGNORECASE)),
    ]

    def __init__(self, filepath: str|Path):
        self.__filepath: Path = Path(filepath)
        self.__data = {'table': []}


    def get_table(self, string: str, string2: str, table_len: int) -> dict:
        id_text_re = re.compile(r'^(\d+)\s*(.*)$', re.S)
        car_vin_re = re.compile(r'[A-Z0-9]{5,}')

        m1 = id_text_re.match(string.strip())
        if m1:
            id = m1.group(1)
            name = m1.group(2).replace('\n', ' ').replace('\\', ', ')

            prices = string2.rstrip('\n').split('\n')

            raw_data = [id, name] + prices
        else: return {}

        if len(raw_data) != table_len:
            return {}

        return dict(zip(self.TABLE_FIELDS, raw_data)) | {'current_car_vin': car_vin_re.search(name).group(0)}


    def get_text_data(self, field: str|list, reg: re.Pattern|None, string: str) -> dict:
        if type(field) == str and type(reg) == re.Pattern:
            match = reg.search(string)
            if match:
                return {field: match.group(1)}
            
        if type(field) == list and reg is None:
            data: dict = {}
            for field_name, patter in field:
                match = patter.search(string)
                if match: data[field_name] = match.group(1)

            return data


    def parse(self):
        self.__data = {'table': []}
        doc = pymupdf.open(self.__filepath)

        for page in doc:
            blocks_sorted = sorted(
                page.get_text("blocks"),
                key=lambda b: (round(b[1], 1), round(b[0], 1))
            )

            i = 0
            n = len(blocks_sorted)

            for pattern_field in self.REG_FIELDS:
                while i < n:
                    line = blocks_sorted[i][4]

                    # Get value
                    if isinstance(pattern_field, tuple):
                        field, pattern = pattern_field
                        field_data = self.get_text_data(field, pattern, line)
                        i += 1
                        if field_data:
                            self.__data.update(field_data)
                            break
                        continue

                    # Get few values in one line
                    if isinstance(pattern_field, list):
                        field_data = self.get_text_data(pattern_field, None, line)
                        i += 1
                        if field_data:
                            self.__data.update(field_data)
                            break
                        continue

                    #Get Table
                    if isinstance(pattern_field, re.Pattern):
                        match = pattern_field.match(line)
                        i += 1
                        if match:
                            while i + 1 < n:
                                row = self.get_table(
                                    blocks_sorted[i][4],
                                    blocks_sorted[i + 1][4],
                                    len(self.TABLE_FIELDS)
                                )
                                if row:
                                    self.__data['table'].append(row)
                                    i += 2
                                    continue
                                break
                            break

        return self.__data