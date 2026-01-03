from django.core.management.base import BaseCommand
from core.constants import test_schema_service


class Command(BaseCommand):
    help = "Calc basic schema to check next car service by millage"

    def handle(self, *args, **options):
        schema_service_data = test_schema_service.get("services")

        if not schema_service_data:
            self.stdout.write(self.style.WARNING("No services found"))
            return
        current_mileage = 200_000
        
        for service in schema_service_data:
            last_service = service.get("last_service_km")
            interval = service.get("interval_km")
            if last_service == 0:
                service["status"] = "UNKNOWN"
                service["next_service"] = None
                self.stdout.write(str(service))
                continue

            next_service = last_service + interval
            service["next_service"]=next_service

            if next_service <= 0:
                service["status"]="IMPORTANT"
            else:
                service["status"]="PLANNED"
            self.stdout.write(str(service))

        self.stdout.write(self.style.SUCCESS("Done"))
