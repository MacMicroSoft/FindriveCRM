from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, CreateView, ListView, View, TemplateView, DeleteView
from django.shortcuts import get_object_or_404
from .forms import AddCarForm, OwnerForm, OutlayFrom
from .services import get_cars_data, create_outlay, get_outlays, get_outlay_form_data, get_outlay, update_outlay
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from .mixins import RoleRequiredMixin
from django.shortcuts import render, redirect
from pprint import pprint
from .models import Outlay


class DashboardView(LoginRequiredMixin, View):
    template_name = "dashboard.html"

    def get(self,request):
        context = {}
        cars_active = get_cars_data()
        context['cars_active'] = cars_active
        context['form'] = AddCarForm()
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = AddCarForm(request.POST)

        if form.is_valid():
            car = form.save()
            return JsonResponse({
                "status": "ok",
                "id": car.uuid,
                "message": "Авто успішно додано!"
            })

        return JsonResponse({
            "status": "error",
            "errors": form.errors
        }, status=400)


class OutlayView(LoginRequiredMixin, View):
    template_name = "outlay.html"

    def get(self, request):
        context = {}
        context['form'] = OutlayFrom()
        context['outlays'] = get_outlays()

        return render(request, self.template_name, context)
    

    def post(self, request):
        form = OutlayFrom(request.POST)

        if form.is_valid():
            outlay_obj = create_outlay(
                type = form.cleaned_data.get('service_type'),
                category = form.cleaned_data.get('category'),
                category_name = form.cleaned_data.get('category_name'),
                service_name = form.cleaned_data.get('service_name'),
                description = form.cleaned_data.get('description'),
                cars = form.cleaned_data.get('car'),
                created_at = form.cleaned_data.get('date'),
                price_per_item = form.cleaned_data.get('price_per_item'),
                item_count = form.cleaned_data.get('item_count'),
                full_price = form.cleaned_data.get('full_price'),
            )
        return JsonResponse({
            'status': 'ok'
        })

class OutlatDetailView(LoginRequiredMixin, View):
    template_name = "outlay_detail.html"
    def get(self, request, pk):
        context = {}
        context['form'] = get_outlay_form_data(pk)
        context['outlay_uuid'] = pk
        return render(request, self.template_name, context)

    def post(self, request, pk):
        form = OutlayFrom(request.POST)

        if form.is_valid():
            outlay = update_outlay(pk, form)
            return redirect("outlay_detail", pk=pk)

        return render(request, self.template_name, {
            "form": form,
            "outlay": outlay,
        })

class OutlayDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        outlay = get_object_or_404(Outlay, pk=pk)
        outlay.delete()
        return redirect("outlay")


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
