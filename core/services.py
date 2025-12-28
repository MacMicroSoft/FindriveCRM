import logging
from typing import Any

from django.db.models import F, Value, Case, When, CharField
from django.db.models.functions import Concat
from .forms import OutlayFrom
from django.db import transaction

from .models import Owner, Car, Outlay, OutlayAmount, OutlayCategoryChoice, OutlayTypeChoice, CarStatusChoice, CarPhoto, Chat, Message, MessageImage, SenderChoice

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


def pdf_parser(filepath) -> dict:
    """
    Parse PDF invoice file.
    
    Note: Requires pdfplumber, tabula-py, and pandas packages.
    These are optional dependencies and should be installed separately.
    """
    try:
        import pdfplumber
        import re 
        import tabula
        import pandas as pd
    except ImportError as e:
        raise ImportError(
            f"PDF parsing requires additional packages: pdfplumber, tabula-py, pandas. "
            f"Install them with: poetry add pdfplumber tabula-py pandas. "
            f"Original error: {e}"
        )
    
    TABLE_FIELDS = ("id", "item_name", "amount", "price_netto", "price_netto2", "tax_percent", "tax_price", "price_brutto")

    tables = tabula.read_pdf(filepath, pages="1", lattice=True)
    df = tables[0]
    df.columns = TABLE_FIELDS
    first_col = df.columns[0]
    df_filtered = df[pd.to_numeric(df[first_col], errors="coerce").notna()]
    table = df_filtered.to_dict(orient="records")

    reg_values = [
        ("invoice_number", re.compile(r"Faktura\s+numer\s+([A-Z\d/]+)", re.IGNORECASE)),
        ("sale_date", re.compile(r"Data\s+wystawienia:\s+Puchały,\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)),
        ("sold_date_limit", re.compile(r"Data\s+sprzedaży:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)),
        ("payment_date_limit", re.compile(r"Termin\s+płatności:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)),
        ("payment", re.compile(r"Płatność:\s*([A-ZĄĆĘŁŃÓŚŻŹ]*)", re.IGNORECASE)),
        ("company_nip", re.compile(r"NIP\s+(\d+)", re.IGNORECASE)),
        ("company_bdo", re.compile(r"BDO\s+(\d+)", re.IGNORECASE)),
        ("price_netto", re.compile(r"Wartość netto\s+([\d,\s]*[\d,]*)\s+", re.IGNORECASE)),
        ("price_vat", re.compile(r"Wartość VAT\s+([\d,\s]*[\d,]*)\s+", re.IGNORECASE)),
        ("price_brutto", re.compile(r"Wartość brutto\s+([\d,\s]*[\d,]*)\s+", re.IGNORECASE)),
        ("to_pay", re.compile(r"Do zapłaty\s+([\d,\s]*[\d,]*)\s+", re.IGNORECASE)),
    ]

    str_data = {}

    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            for line in text.split("\n"):
                for key, pattern in reg_values:
                    match = pattern.search(line)
                    if match:
                        str_data[key] = match.group(1)

    return {
        "table": table,
        "str_data": str_data,
    }


def get_chat_list() -> list[dict]:
    return Chat.objects.filter(is_active=True).all()


def get_chat_info(chat_id):
    print(chat_id)
    chat = Chat.objects.values().get(tg_chat_id = chat_id)
    messages = Message.objects.filter(chat=chat.get('uuid'))

    return {**chat, "messages": messages}


def create_message(chat: Chat, message: str, from_, is_recived: bool=False) -> Message:
    msg =  Message.objects.create(
        chat = chat,
        sender = SenderChoice(from_),
        message = message,
        sended = is_recived
    )

    return {
        "sender": msg.sender,
        "message": msg.message,
        "created_at": msg.created_at.isoformat(),
    }


def creat_chat(chat_id: int, user_first: str, user_last: str, tagname: str) -> Chat:
    if not Chat.objects.filter(tg_chat_id=chat_id):
        return Chat.objects.create(
            tg_chat_id = chat_id,
            user_first = user_first,
            user_last = user_last,
            tagname = tagname,
        )
    
    return None
    

def get_chat(chat_id: int) -> Chat:
    return Chat.objects.get(tg_chat_id=chat_id)