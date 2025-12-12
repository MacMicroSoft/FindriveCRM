from .models import Owner
from django.db.models import F, Value, Case, When, CharField
from django.db.models.functions import Concat


def get_owners_choice() -> list[tuple]:
    owners = Owner.objects.annotate(
        full_name=Concat(F("first_name"), Value(" "), F("last_name"))
    ).values("uuid", "full_name")

    return [(o["uuid"], o["full_name"]) for o in owners]