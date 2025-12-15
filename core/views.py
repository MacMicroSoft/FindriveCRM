import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import JsonResponse
from django.views.generic import (
    DetailView,
    ListView,
    TemplateView,
    View,
)

from .forms import AddCarForm, OwnerForm, ServiceForm
from .models import Car, CarPhoto, Owner, Service
from .services import create_car_with_photos, delete_car, update_car_with_photos

logger = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cars_active = (
            Car.objects.filter(status="Active").select_related("owner").order_by("-created_at")
        )
        cars_pending = (
            Car.objects.filter(status__in=["Await", "Processing"])
            .select_related("owner")
            .order_by("-created_at")
        )

        context["cars_active"] = cars_active
        context["cars_pending"] = cars_pending
        context["form"] = AddCarForm()
        return context


class AddCarView(View):
    def post(self, request):
        logger.info(f"Request method: {request.method}")

        result = create_car_with_photos(
            form_data=request.POST,
            files=request.FILES,
            form_class=AddCarForm,
        )

        if result["success"]:
            return JsonResponse(
                {
                    "status": "ok",
                    "id": str(result["car"].uuid),
                    "message": result["message"],
                }
            )
        status_code = 500 if "__all__" in result["errors"] else 400
        return JsonResponse(
            {
                "status": "error",
                "errors": result["errors"],
            },
            status=status_code,
        )


class CarDetailView(LoginRequiredMixin, DetailView):
    model = Car
    template_name = "car/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AddCarForm(instance=self.object)
        context["photos"] = CarPhoto.objects.filter(car=self.object)
        return context


class CarDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        logger.info(f"Request method: {request.method}, UUID: {pk}")

        result = delete_car(car_uuid=str(pk))

        if result["success"]:
            return JsonResponse(
                {
                    "status": "ok",
                    "message": result["message"],
                }
            )
        status_code = 404 if "not found" in result["message"].lower() else 500
        return JsonResponse(
            {
                "status": "error",
                "errors": result["errors"],
            },
            status=status_code,
        )

class CarSaveView(LoginRequiredMixin, View):
    pass

class CarUnsaveView(LoginRequiredMixin, View):
    pass

class CarSaveListView(LoginRequiredMixin, ListView):
    model = Car
    template_name = "car/save_list.html"

    def get_queryset(self):
        user=self.request.user
        cars= user.cars.filter(is_saved=True).order_by("-created_at")
        return cars

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AddCarForm()

class CarUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        logger.info(f"Request method: {request.method}, UUID: {pk}")

        result = update_car_with_photos(
            car_uuid=str(pk),
            form_data=request.POST,
            files=request.FILES,
            form_class=AddCarForm,
        )

        if result["success"]:
            return JsonResponse(
                {
                    "status": "ok",
                    "id": str(result["car"].uuid),
                    "message": result["message"],
                }
            )
        status_code = (
            404
            if "not found" in result["message"].lower()
            else (500 if "__all__" in result["errors"] else 400)
        )
        return JsonResponse(
            {
                "status": "error",
                "errors": result["errors"],
            },
            status=status_code,
        )


class OwnerListView(LoginRequiredMixin, ListView):
    model = Owner
    paginate_by = 20
    template_name = "owner/list.html"

    def get_queryset(self):
        return Owner.objects.annotate(cars_count=Count("cars")).order_by(
            "first_name", "last_name"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = OwnerForm()
        return context


class OwnerCreateView(LoginRequiredMixin, View):
    def post(self, request):
        form = OwnerForm(request.POST)

        if form.is_valid():
            owner = form.save()
            return JsonResponse(
                {
                    "status": "ok",
                    "id": str(owner.uuid),
                    "message": "Owner successfully added!",
                }
            )

        return JsonResponse(
            {
                "status": "error",
                "errors": form.errors,
            },
            status=400,
        )


class OwnerUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            owner = Owner.objects.get(uuid=pk)
        except Owner.DoesNotExist:
            return JsonResponse(
                {
                    "status": "error",
                    "errors": {"__all__": ["Owner not found"]},
                },
                status=404,
            )

        form = OwnerForm(request.POST, instance=owner)

        if form.is_valid():
            owner = form.save()
            return JsonResponse(
                {
                    "status": "ok",
                    "id": str(owner.uuid),
                    "message": "Owner successfully updated!",
                }
            )

        return JsonResponse(
            {
                "status": "error",
                "errors": form.errors,
            },
            status=400,
        )


class OwnerDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            owner = Owner.objects.get(uuid=pk)
            owner.delete()
            return JsonResponse(
                {
                    "status": "ok",
                    "message": "Owner successfully deleted!",
                }
            )
        except Owner.DoesNotExist:
            return JsonResponse(
                {
                    "status": "error",
                    "errors": {"__all__": ["Owner not found"]},
                },
                status=404,
            )


class OwnerDetailView(LoginRequiredMixin, DetailView):
    model = Owner
    template_name = "owner/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = OwnerForm(instance=self.object)
        return context


class ServiceListView(LoginRequiredMixin, ListView):
    model = Service
    template_name = "service/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ServiceForm()
        return context


class ServiceCreateView(LoginRequiredMixin, View):
    def post(self, request):
        form = ServiceForm(request.POST)

        if form.is_valid():
            service = form.save()
            return JsonResponse(
                {
                    "status": "ok",
                    "id": str(service.uuid),
                    "message": "Service successfully added!",
                }
            )

        return JsonResponse(
            {
                "status": "error",
                "errors": form.errors,
            },
            status=400,
        )


class ServiceUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            service = Service.objects.get(uuid=pk)
        except Service.DoesNotExist:
            return JsonResponse(
                {
                    "status": "error",
                    "errors": {"__all__": ["Service not found"]},
                },
                status=404,
            )

        form = ServiceForm(request.POST, instance=service)

        if form.is_valid():
            service = form.save()
            return JsonResponse(
                {
                    "status": "ok",
                    "id": str(service.uuid),
                    "message": "Service successfully updated!",
                }
            )

        return JsonResponse(
            {
                "status": "error",
                "errors": form.errors,
            },
            status=400,
        )


class ServiceDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            service = Service.objects.get(uuid=pk)
            service.delete()
            return JsonResponse(
                {
                    "status": "ok",
                    "message": "Service successfully deleted!",
                }
            )
        except Service.DoesNotExist:
            return JsonResponse(
                {
                    "status": "error",
                    "errors": {"__all__": ["Service not found"]},
                },
                status=404,
            )


class ServiceDetailView(LoginRequiredMixin, DetailView):
    model = Service
    template_name = "service/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ServiceForm(instance=self.object)
        return context
