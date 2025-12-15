import logging
from typing import Any

from django.db.models import F, Value
from django.db.models.functions import Concat

from .models import Car, CarPhoto, Owner

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
