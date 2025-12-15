import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, CreateView, ListView, View, TemplateView
from django.shortcuts import get_object_or_404
from .forms import AddCarForm, OwnerForm
from .models import Car, Owner
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from .mixins import RoleRequiredMixin
from django.shortcuts import render, redirect


class DashboardView(LoginRequiredMixin, View):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cars_active = Car.objects.filter(status="Active").values('mark', 'model', 'year', 'vin_code', 'status', 'license_plate')
        context['cars_active'] = cars_active
        context['form'] = AddCarForm()
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
            car: Car = form.save()
            return JsonResponse({
                "status": "ok",
                "id": car.uuid,
                "message": "Авто успішно додано!"
            })

        return JsonResponse({
            "status": "error",
            "errors": form.errors
        }, status=400)

# class NotificationsView(LoginRequiredMixin, TemplateView):
#     template_name = "notifications.html"

# class ChatView(LoginRequiredMixin, TemplateView):
#     template_name = "chat.html"

# class OwnerCreateAjaxView(RoleRequiredMixin, View):
#     required_roles = ["auto_manager"]

#     def post(self, request, *args, **kwargs):
#         form = OwnerForm(request.POST)
#         if form.is_valid():
#             owner = form.save()
#             return JsonResponse({
#                 "success": True,
#                 "id": owner.pk,
#                 "name": f"{owner.first_name} {owner.last_name}"
#             })
#         return JsonResponse({"success": False, "errors": form.errors}, status=400)

# class CarDetailView(RoleRequiredMixin, DetailView):
#     model = Car
#     template_name = "cars/detail.html"
#     required_roles = ["auto_manager"]

#     def get_queryset(self):
#         return Car.objects.all()

# class CarCreateView(RoleRequiredMixin, CreateView):
#     model = Car
#     form_class = CarForm
#     template_name = "cars/create.html"
#     required_roles = ["auto_manager"]


#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["owner_form"] = OwnerForm()
#         return context

#     def get_success_url(self):
#         return reverse("car_detail", kwargs={"pk": self.object.pk})

# class CarListView(RoleRequiredMixin, ListView):
#     model = Car
#     template_name = "cars/list.html"
#     required_roles = ["auto_manager"]
#     paginate_by = 20


# class CreateOwnerView(RoleRequiredMixin, CreateView):
#     model = Owner
#     form_class = OwnerForm
#     required_roles = ["auto_manager"]
#     template_name = "owner/create.html"
#     success_url = reverse_lazy("car_create")

#     def form_valid(self, form):
#         return super().form_valid(form)

# class OwnerListView(RoleRequiredMixin, ListView):
#     model = Owner
#     template_name = "owner/list.html"
#     required_roles = ["auto_manager"]
#     paginate_by = 20
