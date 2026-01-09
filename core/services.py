import logging
from typing import Any
from datetime import date

from django.db.models import F, Value, Case, When, CharField
from django.db.models.functions import Concat
from .forms import OutlayFrom
from django.db import transaction
import pymupdf
import pdfplumber
from pathlib import Path
import re

from .models import Owner, Car, Outlay, OutlayAmount, OutlayCategoryChoice, OutlayTypeChoice, CarStatusChoice, CarPhoto, CarServiceState, ServiceEvent

logger = logging.getLogger(__name__)


def get_owners_choice() -> list[tuple]:
    owners = Owner.objects.annotate(
        full_name=Concat(F("first_name"), Value(" "), F("last_name")),
    ).values("uuid", "full_name")

    return [(o["uuid"], o["full_name"]) for o in owners]

def create_car_with_photos(
    form_data: dict[str, Any],
    files: dict[str, Any],
    form_class,
) -> dict[str, Any]:
    """
    Create a car with photos.

    Args:
        form_data: POST form data
        files: FILES data (photos)
        form_class: Form class for validation

    Returns:
        Dict with keys:
            - success: bool - whether creation was successful
            - car: Car or None - created car
            - errors: Dict - validation errors
            - message: str - message
    """
    logger.info("=== Starting car creation process ===")
    logger.info(f"Has FILES: {bool(files)}")
    logger.info(f"FILES keys: {list(files.keys()) if files else 'None'}")
    logger.info(f"POST keys: {list(form_data.keys())}")

    for key, value in form_data.items():
        logger.debug(f"POST[{key}]: {value}")

    if files:
        for key in files:
            files_list = (
                files.getlist(key)
                if hasattr(files, "getlist")
                else [files.get(key)]
                if files.get(key)
                else []
            )
            logger.info(f"FILES[{key}]: {len(files_list)} file(s)")
            for i, file in enumerate(files_list):
                if file:
                    logger.info(
                        f"  File {i + 1}: {file.name}, size: {file.size} bytes, "
                        f"type: {file.content_type}",
                    )
    else:
        logger.warning(
            "WARNING: request.FILES is empty! Form may not have enctype='multipart/form-data'",
        )

    try:
        form = form_class(form_data, files)
        logger.info("Form created")

        is_valid = form.is_valid()
        logger.info(f"Form is valid: {is_valid}")

        if not is_valid:
            logger.error("ERROR: Form is invalid")
            logger.error(f"Form errors: {form.errors}")
            logger.error(f"Non-field errors: {form.non_field_errors()}")
            for field, errors in form.errors.items():
                logger.error(f"  {field}: {errors}")

            return {
                "success": False,
                "car": None,
                "errors": form.errors,
                "message": "Form validation error",
            }

        logger.info("OK: Form is valid")
        logger.info(f"Cleaned data keys: {list(form.cleaned_data.keys())}")

        car: Car = form.save()
        logger.info(f"OK: Car created: {car.uuid}")

        # Process photos
        photos = []
        if hasattr(files, "getlist"):
            photos = files.getlist("photos")
        elif files.get("photos"):
            photos = (
                [files.get("photos")]
                if not isinstance(files.get("photos"), list)
                else files.get("photos")
            )

        logger.info(f"Found {len(photos)} photo(s) in request.FILES.getlist('photos')")

        if not photos:
            logger.warning(
                "WARNING: Photos not found in request.FILES.getlist('photos')",
            )
            try:
                photos = form.cleaned_data.get("photos", [])
                logger.info(f"Attempted to get from cleaned_data: {type(photos)}")
                if not isinstance(photos, list):
                    photos = [photos] if photos else []
                logger.info(f"After conversion: {len(photos)} photo(s)")
            except Exception as e:
                logger.error(f"ERROR: Error getting photos from cleaned_data: {e}")
                photos = []

        if photos and len(photos) > 3:
            logger.warning(f"WARNING: Too many photos: {len(photos)} (max 3)")
            return {
                "success": False,
                "car": None,
                "errors": {"photos": ["Maximum 3 photos allowed"]},
                "message": "Too many photos",
            }

        if photos:
            logger.info(f"Saving {len(photos)} photo(s)...")
            for index, photo in enumerate(photos[:3]):
                if photo:
                    try:
                        CarPhoto.objects.create(
                            car=car,
                            photo=photo,
                            order=index,
                        )
                        logger.info(f"OK: Photo {index + 1} saved: {photo.name}")
                    except Exception as e:
                        logger.error(f"ERROR: Error saving photo {index + 1}: {e}")
        else:
            logger.info(
                "INFO: Photos were not uploaded (this is normal, field is optional)",
            )

        logger.info("=== Successful completion ===")
        return {
            "success": True,
            "car": car,
            "errors": {},
            "message": "Car successfully added!",
        }

    except Exception as e:
        logger.exception(f"CRITICAL ERROR: Critical error processing form: {e}")
        return {
            "success": False,
            "car": None,
            "errors": {"__all__": [f"Internal server error: {e!s}"]},
            "message": "Internal server error",
        }


def update_car_with_photos(
    car_uuid: str,
    form_data: dict[str, Any],
    files: dict[str, Any],
    form_class,
) -> dict[str, Any]:
    """
    Update a car with photos.

    Args:
        car_uuid: UUID of car to update
        form_data: POST form data
        files: FILES data (photos)
        form_class: Form class for validation

    Returns:
        Dict with keys:
            - success: bool - whether update was successful
            - car: Car or None - updated car
            - errors: Dict - validation errors
            - message: str - message
    """
    logger.info(f"=== Starting car update process {car_uuid} ===")
    logger.info(f"Has FILES: {bool(files)}")
    logger.info(f"FILES keys: {list(files.keys()) if files else 'None'}")
    logger.info(f"POST keys: {list(form_data.keys())}")

    try:
        car = Car.objects.get(uuid=car_uuid)
        logger.info(f"Car found: {car}")
    except Car.DoesNotExist:
        logger.error(f"ERROR: Car with UUID {car_uuid} not found")
        return {
            "success": False,
            "car": None,
            "errors": {"__all__": ["Car not found"]},
            "message": "Car not found",
        }

    for key, value in form_data.items():
        logger.debug(f"POST[{key}]: {value}")

    if files:
        for key in files:
            files_list = (
                files.getlist(key)
                if hasattr(files, "getlist")
                else [files.get(key)]
                if files.get(key)
                else []
            )
            logger.info(f"FILES[{key}]: {len(files_list)} file(s)")
            for i, file in enumerate(files_list):
                if file:
                    logger.info(
                        f"  File {i + 1}: {file.name}, size: {file.size} bytes, "
                        f"type: {file.content_type}",
                    )

    try:
        form = form_class(form_data, files, instance=car)
        logger.info("Form created with instance")

        is_valid = form.is_valid()
        logger.info(f"Form is valid: {is_valid}")

        if not is_valid:
            logger.error("ERROR: Form is invalid")
            logger.error(f"Form errors: {form.errors}")
            logger.error(f"Non-field errors: {form.non_field_errors()}")
            for field, errors in form.errors.items():
                logger.error(f"  {field}: {errors}")

            return {
                "success": False,
                "car": None,
                "errors": form.errors,
                "message": "Form validation error",
            }

        logger.info("OK: Form is valid")
        logger.info(f"Cleaned data keys: {list(form.cleaned_data.keys())}")

        car = form.save()
        logger.info(f"OK: Car updated: {car.uuid}")

        # Process new photos (if any)
        photos = []
        if hasattr(files, "getlist"):
            photos = files.getlist("photos")
        elif files.get("photos"):
            photos = (
                [files.get("photos")]
                if not isinstance(files.get("photos"), list)
                else files.get("photos")
            )

        logger.info(f"Found {len(photos)} new photo(s)")

        if photos and len(photos) > 3:
            logger.warning(f"WARNING: Too many photos: {len(photos)} (max 3)")
            return {
                "success": False,
                "car": None,
                "errors": {"photos": ["Maximum 3 photos allowed"]},
                "message": "Too many photos",
            }

        # Get current photos
        existing_photos_count = CarPhoto.objects.filter(car=car).count()
        logger.info(f"Current photos: {existing_photos_count}")

        if photos:
            logger.info(f"Saving {len(photos)} new photo(s)...")
            # Delete old photos if new ones are added
            if existing_photos_count > 0:
                CarPhoto.objects.filter(car=car).delete()
                logger.info("Old photos deleted")

            for index, photo in enumerate(photos[:3]):
                if photo:
                    try:
                        CarPhoto.objects.create(
                            car=car,
                            photo=photo,
                            order=index,
                        )
                        logger.info(f"OK: Photo {index + 1} saved: {photo.name}")
                    except Exception as e:
                        logger.error(f"ERROR: Error saving photo {index + 1}: {e}")
        else:
            logger.info("New photos not uploaded (old photos remain)")

        logger.info("=== Successful update completion ===")
        return {
            "success": True,
            "car": car,
            "errors": {},
            "message": "Car successfully updated!",
        }

    except Exception as e:
        logger.exception(f"CRITICAL ERROR: Critical error updating car: {e}")
        return {
            "success": False,
            "car": None,
            "errors": {"__all__": [f"Internal server error: {e!s}"]},
            "message": "Internal server error",
        }


def delete_car(car_uuid: str) -> dict[str, Any]:
    """
    Delete a car.

    Args:
        car_uuid: UUID of car to delete

    Returns:
        Dict with keys:
            - success: bool - whether deletion was successful
            - errors: Dict - errors
            - message: str - message
    """
    logger.info(f"=== Starting car deletion process {car_uuid} ===")

    try:
        car = Car.objects.get(uuid=car_uuid)
        logger.info(f"Car found: {car}")

        # Delete photos before deleting car
        photos_count = CarPhoto.objects.filter(car=car).count()
        if photos_count > 0:
            CarPhoto.objects.filter(car=car).delete()
            logger.info(f"Deleted {photos_count} photo(s)")

        car.delete()
        logger.info(f"OK: Car {car_uuid} deleted")
        logger.info("=== Successful deletion completion ===")

        return {
            "success": True,
            "errors": {},
            "message": "Car successfully deleted!",
        }

    except Car.DoesNotExist:
        logger.error(f"ERROR: Car with UUID {car_uuid} not found")
        return {
            "success": False,
            "errors": {"__all__": ["Car not found"]},
            "message": "Car not found",
        }
    except Exception as e:
        logger.exception(f"CRITICAL ERROR: Critical error deleting car: {e}")
        return {
            "success": False,
            "errors": {"__all__": [f"Internal server error: {e!s}"]},
            "message": "Internal server error",
        }


def get_cars_data(status: str = None) -> list[dict]:
    if status == None:
        status = CarStatusChoice.ACTIVE
    return list(Car.objects
        .filter(status=status)
        .values("mark", "model", "year", "vin_code", "status", "license_plate")
    )


def get_car_param_to_view(car: Car) -> dict:
    return car.values("mark", "model", "year", "vin_code", "status", "license_plate")


def create_outlay(
    type: str,
    name: str,
    car: Car,  # Changed from cars: list[Car] to car: Car
    price_per_item: float, 
    item_count: int,
    created_at,
    full_price: int = None,
    category: str = None,
    category_name: str = None,
    service_name: str = None,
    comment: str = None,
    description: str = None,  # For backward compatibility
) -> Outlay:
    if full_price:
        outlay_amout_obj: OutlayAmount = OutlayAmount.objects.create(
            full_price=full_price
        )
    else:
        outlay_amout_obj: OutlayAmount = OutlayAmount.objects.create(
            price_per_item=price_per_item,
            item_count=item_count
        )

    # For service type, don't set category (it should be None)
    # For other type, set category if provided
    final_category = None
    if type == 'service':
        final_category = None  # Service type doesn't have category
    else:
        final_category = category if category else None
    
    outlay_obj: Outlay = Outlay.objects.create(
        type=type,
        category=final_category,
        category_name=category_name if type != 'service' else None,
        service_name=service_name,
        name=name,
        comment=comment,
        description=description,  # For backward compatibility
        amount=outlay_amout_obj,
        created_at=created_at
    )
    outlay_obj.cars.set([car])  # Set single car as list

    return outlay_obj


def get_outlays() -> list[dict]:
    return Outlay.objects.select_related("outlay_cars", "amount").values(
        "cars__mark", "cars__model", "cars__license_plate",
        "uuid", "category", "category_name", "name", "comment", "description", "created_at", "updated_at",
        "amount__price_per_item", "amount__item_count", "amount__full_price",
    )


def get_outlay_form_data(uuid):
    outlay: Outlay = Outlay.objects.get(uuid=uuid)
    amount: OutlayAmount = outlay.amount
    # Get first car (since now it's single car per outlay)
    car = outlay.cars.first()
    form = OutlayFrom(initial={
        "car": car,  # Single car instead of list
        "service_type": outlay.type,
        "category": outlay.category,
        "category_name": outlay.category_name,
        "service_name": outlay.service_name,
        "name": outlay.name or (outlay.description[:255] if outlay.description else ""),
        "comment": outlay.comment,
        "description": outlay.description,  # For backward compatibility
        "date": outlay.created_at if not outlay.updated_at else outlay.updated_at,
        "price_type": "full" if amount.full_price else "part",
        "full_price": amount.full_price,
        "price_per_item": amount.price_per_item,
        "item_count": amount.item_count,
    })
    return form


def get_outlay(uuid) -> Outlay:
    return Outlay.objects.get(uuid=uuid)


def update_outlay(uuid, form: OutlayFrom) -> Outlay:
    outlay = Outlay.objects.get(uuid=uuid)
    amount: OutlayAmount = outlay.amount

    cd = form.cleaned_data

    with transaction.atomic():
        outlay.type = cd["service_type"]
        
        # For service type, don't set category (it should be None)
        # For other type, set category if provided
        if cd["service_type"] == 'service':
            outlay.category = None
            outlay.category_name = None
        else:
            outlay.category = cd.get("category")
            outlay.category_name = cd.get("category_name")
        
        outlay.service_name = cd.get("service_name")
        outlay.name = cd.get("name", "")
        outlay.comment = cd.get("comment")
        outlay.description = cd.get("description")  # For backward compatibility
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

        outlay.cars.set([cd["car"]])  # Set single car as list

    return outlay


def to_float_pl(value: str) -> float:
    """
    Convert Polish number format to float.
    '1 100,00' -> 1100.0
    '1 000,00' -> 1000.0
    """
    if value is None:
        return 0.0
    value = value.replace("\u00a0", " ")
    value = re.sub(r"[^\d,\.]", "", value)
    value = value.replace(" ", "")
    if "," in value:
        value = value.replace(",", ".")
    return float(value)


def decode_unicode_escapes(text: str) -> str:
    """
    Decode Unicode escape sequences in text.
    '\\u005C' -> '\\'
    '\\u0022' -> '"'
    Handles both raw strings with \\u and actual escape sequences stored in database.
    """
    if not text:
        return text
    
    try:
        # Replace Unicode escape sequences using regex
        def replace_unicode(match):
            code = int(match.group(1), 16)
            return chr(code)
        
        # Pattern to match \uXXXX where XXXX is 4 hex digits
        # This handles the literal string "\\u005C" as stored in database
        pattern = r'\\u([0-9a-fA-F]{4})'
        
        # Check if text contains Unicode escape sequences
        if '\\u' in text:
            # Decode all \uXXXX sequences
            text = re.sub(pattern, replace_unicode, text)
        
    except Exception as e:
        logger.warning(f"Error decoding Unicode escapes: {e}")
        # Fallback: manual replacement of common sequences
        try:
            text = text.replace('\\u005C', '\\')  # Backslash
            text = text.replace('\\u0022', '"')    # Double quote
            text = text.replace('\\u0027', "'")    # Single quote
            text = text.replace('\\u000A', '\n')   # Newline
            text = text.replace('\\u000D', '\r')   # Carriage return
            text = text.replace('\\u0009', '\t')   # Tab
        except Exception:
            pass
    
    return text


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

    def _validate_row(self, row: dict) -> dict:
        """Validate row calculations and return validation errors."""
        errors = {}
        tolerance = 0.01  # Tolerance for floating point comparison
        
        price_netto = row.get('price_netto', 0.0)
        tax_price = row.get('tax_price', 0.0)
        price_brutto = row.get('price_brutto', 0.0)
        tax_percent = row.get('tax_percent', 0)
        
        # Check: price_netto + tax_price = price_brutto
        expected_brutto = price_netto + tax_price
        if abs(expected_brutto - price_brutto) > tolerance:
            errors['price_brutto'] = f'Очікується {expected_brutto:.2f}, знайдено {price_brutto:.2f}'
            errors['tax_price'] = 'Не відповідає розрахунку'
        
        # Check: price_netto * (1 + tax_percent/100) = price_brutto
        if tax_percent > 0:
            expected_brutto_from_percent = price_netto * (1 + tax_percent / 100)
            if abs(expected_brutto_from_percent - price_brutto) > tolerance:
                errors['tax_percent'] = f'Очікується {expected_brutto_from_percent:.2f}, знайдено {price_brutto:.2f}'
                if 'price_brutto' not in errors:
                    errors['price_brutto'] = 'Не відповідає розрахунку з ПДВ'
        
        return errors

    def _extract_table_with_pdfplumber(self) -> list:
        """Extract table data using pdfplumber."""
        rows = []
        car_vin_re = re.compile(r'[A-Z0-9]{5,}')

        with pdfplumber.open(self.__filepath) as pdf:
            for page_no, page in enumerate(pdf.pages, start=1):
                logger.info("Processing page %d", page_no)

                table = page.extract_table({
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                    "intersection_tolerance": 5,
                    "snap_tolerance": 5,
                    "join_tolerance": 5,
                })

                if not table:
                    logger.warning("No table found on page %d", page_no)
                    continue

                headers = [h.strip() if h else "" for h in table[0]]

                if len(headers) < 8:
                    logger.warning("Unexpected header format: %s", headers)
                    continue

                for raw in table[1:]:
                    if not raw or not raw[0] or not raw[0].strip().isdigit():
                        continue

                    try:
                        item_name = " ".join(filter(None, raw[1].split())) if raw[1] else ""
                        # Decode Unicode escape sequences
                        item_name = decode_unicode_escapes(item_name)
                        # Truncate item_name to 1000 characters to avoid database error
                        if len(item_name) > 1000:
                            item_name = item_name[:997] + "..."
                        
                        row = {
                            'id': int(raw[0]),
                            'item_name': item_name,
                            'amount': int(re.sub(r"[^\d]", "", raw[2])) if raw[2] else 1,
                            'price_netto': to_float_pl(raw[3]) if raw[3] else 0.0,
                            'price_netto2': to_float_pl(raw[4]) if raw[4] else 0.0,
                            'tax_percent': int(re.sub(r"[^\d]", "", raw[5])) if raw[5] else 23,
                            'tax_price': to_float_pl(raw[6]) if raw[6] else 0.0,
                            'price_brutto': to_float_pl(raw[7]) if raw[7] else 0.0,
                        }
                        
                        # Extract VIN if present in item_name
                        vin_match = car_vin_re.search(item_name)
                        if vin_match:
                            row['current_car_vin'] = vin_match.group(0)
                        
                        # Validate row calculations
                        validation_errors = self._validate_row(row)
                        if validation_errors:
                            row['validation_errors'] = validation_errors
                        
                        rows.append(row)

                    except Exception as e:
                        logger.warning("Skipped row %s (%s)", raw, e)

        return rows

    def parse(self):
        self.__data = {'table': []}
        
        # Extract non-table data using pymupdf (existing logic)
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

                    if isinstance(pattern_field, tuple):
                        field, pattern = pattern_field
                        field_data = self.get_text_data(field, pattern, line)
                        i += 1
                        if field_data:
                            self.__data.update(field_data)
                            break
                        continue

                    if isinstance(pattern_field, list):
                        field_data = self.get_text_data(pattern_field, None, line)
                        i += 1
                        if field_data:
                            self.__data.update(field_data)
                            break
                        continue

                    if isinstance(pattern_field, re.Pattern):
                        # Skip table header pattern - we'll extract table with pdfplumber
                        i += 1
                        break

        # Extract table data using pdfplumber
        try:
            table_rows = self._extract_table_with_pdfplumber()
            self.__data['table'] = table_rows
            
            # Calculate total from table and compare with PDF total
            total_from_table = sum(row.get('price_brutto', 0.0) for row in table_rows)
            pdf_total = self.__data.get('price_brutto') or self.__data.get('to_pay')
            
            if pdf_total:
                # Convert PDF total to float if it's a string
                if isinstance(pdf_total, str):
                    pdf_total_float = to_float_pl(pdf_total)
                else:
                    pdf_total_float = float(pdf_total)
                
                tolerance = 0.01
                if abs(total_from_table - pdf_total_float) > tolerance:
                    self.__data['total_validation_error'] = {
                        'expected': pdf_total_float,
                        'found': total_from_table,
                        'difference': abs(total_from_table - pdf_total_float)
                    }
            
        except Exception as e:
            logger.error("Error extracting table with pdfplumber: %s", e)
            self.__data['table'] = []

        return self.__data


def create_car_service_plan(plan_schema: dict, current_mileage: int) -> list:
    services = plan_schema.get("services")

    if not services:
        raise ValueError("No services found in schema")

    result = []

    for service in services:
        service = service.copy()

        last_service = service.get("last_service_km", 0)
        interval = service.get("interval_km", 0)

        if last_service == 0:
            service["status"] = "UNKNOWN"
            service["next_service"] = None
            result.append(service)
            continue

        next_service = last_service + interval
        service["next_service"] = next_service

        result.append(service)

    return result

def save_or_update_car_service_state(car, service_plan: dict, mileage: int) -> CarServiceState:
    """Зберегти або оновити CarServiceState з розрахованими сервісами"""
    if mileage is None:
        mileage=Car.objects.filter(car=car).only("mileage")

    if mileage <= 0 or not mileage:
        raise ValueError("Unexpected error with mileage absent")
    
    try:
        calculated_services = create_car_service_plan(
            plan_schema=service_plan,
            current_mileage=mileage,
        )
    except ValueError as exc:
        raise ValueError(str(exc))
    
    service_plan["services"] = calculated_services
    
    try:
        car_service_state = CarServiceState.objects.get(car=car)
        car_service_state.service_plan = service_plan
        car_service_state.mileage = mileage
        car_service_state.save()
    except CarServiceState.DoesNotExist:
        car_service_state = CarServiceState.objects.create(
            car=car,
            service_plan=service_plan,
            mileage=mileage
        )
    
    return car_service_state


@transaction.atomic
def recalculate_car_service_plan(car_id, new_mileage: int):
    schema=(CarServiceState.objects
    .select_for_update()
    .select_related("car")
    .get(car_id=car_id)
)   
    mileage_diff = new_mileage - schema.mileage
    
    if mileage_diff <= 0:
        return schema.service_plan

    services = schema.service_plan.get("services", [])
    updated_services = []

    for service in services:
        service = service.copy()

        next_service = service.get("next_service")

        if next_service is not None:
            service["next_service"] = max(0, next_service - mileage_diff)

        updated_services.append(service)

    schema.service_plan["services"] = updated_services
    schema.mileage = new_mileage
    schema.save(update_fields=["service_plan", "mileage", "updated_at"])

    return updated_services


def create_service_events_from_services(car, services: list, mileage: int):
    """
    Створює ServiceEvent записи безпосередньо зі списку сервісів.
    Враховує всі поля моделі ServiceEvent включаючи статуси.
    
    Args:
        car: Car instance
        services: список сервісів (dict з полями: key, name, interval_km, last_service_km)
        mileage: поточний пробіг автомобіля
    
    Returns:
        list: список створених ServiceEvent об'єктів
    
    Raises:
        ValueError: якщо services порожній або інші помилки
    """
    if not services:
        raise ValueError("Список сервісів не може бути порожнім")
    
    if not isinstance(services, list):
        raise ValueError("services повинно бути списком")
    
    created_events = []
    today = date.today()
    
    for service in services:
        if not isinstance(service, dict):
            continue
        
        # Отримуємо дані з сервісу
        last_service_km = service.get("last_service_km", 0)
        interval_km = service.get("interval_km", 0)
        
        # Визначаємо service_type
        service_type = service.get("name", service.get("key", "Unknown Service"))
        
        # Обмежуємо довжину service_type до 50 символів (максимум для поля)
        if len(service_type) > 50:
            service_type = service_type[:47] + "..."
        
        # Обчислюємо next_service_km
        if last_service_km > 0:
            next_service_km = last_service_km + interval_km
        else:
            # Для невідомих сервісів встановлюємо next_service_km на основі поточного пробігу
            next_service_km = mileage + interval_km if interval_km > 0 else mileage
        
        # Визначаємо статус на основі поточного пробігу та next_service_km
        from .models import ServiceStatusChoice
        
        if last_service_km == 0:
            status = ServiceStatusChoice.UNKNOWN
            is_completed = False
        else:
            # Визначаємо статус на основі поточного пробігу
            # Критично - якщо пробіг перевищив next_service_km більш ніж на 20%
            # Важливо - якщо пробіг наближається до next_service_km (за 10% до або вже перевищив)
            # В Нормі - якщо ще є час до наступного сервісу
            if mileage >= next_service_km * 1.2:  # Перевищено більш ніж на 20%
                status = ServiceStatusChoice.CRITICAL  # Критично
            elif mileage >= next_service_km:  # Перевищено або досягнуто
                status = ServiceStatusChoice.IMPORTANT  # Важливо
            elif mileage > next_service_km - (interval_km * 0.1):  # За 10% до наступного сервісу
                status = ServiceStatusChoice.IMPORTANT  # Важливо
            else:
                status = ServiceStatusChoice.NORMAL  # В Нормі
            
            is_completed = last_service_km > 0
        
        # Перевіряємо, чи не існує вже такий івент (щоб уникнути дублікатів)
        # Використовуємо тільки поля, які точно існують в БД
        existing_event = ServiceEvent.objects.filter(
            car=car,
            service_type=service_type,
            last_service_km=last_service_km
        ).first()
        
        if not existing_event:
            event = ServiceEvent.objects.create(
                car=car,
                service_type=service_type,
                mileage_km=mileage,  # Поточний пробіг автомобіля
                next_service_km=next_service_km,
                last_service_km=last_service_km,
                interval_km=interval_km,
                date=today,
                status=status,
                is_completed=is_completed
            )
            created_events.append(event)
    
    return created_events


def parse_events_for_car_by_json(car, service_plan: dict, mileage: int):
    """
    Дістає всі івенти з JSON service_plan і додає їх в бд до відповідного авто.
    Враховує всі поля моделі ServiceEvent включаючи статуси.
    
    Args:
        car: Car instance
        service_plan: dict з полем "services" (список сервісів з обчисленими next_service)
        mileage: поточний пробіг автомобіля
    
    Returns:
        list: список створених ServiceEvent об'єктів
    
    Raises:
        ValueError: якщо service_plan не містить services або інші помилки
    """
    if not service_plan:
        raise ValueError("service_plan не може бути порожнім")
    
    services = service_plan.get("services", [])
    
    if not services:
        raise ValueError("service_plan не містить поле 'services' або воно порожнє")
    
    # Використовуємо нову функцію для створення івентів
    return create_service_events_from_services(car, services, mileage)
