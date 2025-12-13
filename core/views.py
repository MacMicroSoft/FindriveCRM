from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import JsonResponse
from django.views.generic import (
    DetailView, 
    CreateView, 
    ListView, 
    View, 
    TemplateView, 
    UpdateView, 
    DeleteView
)
from .forms import (
    AddCarForm, 
    OwnerForm, 
    ServiceForm
)
from .models import (
    Car, 
    Owner,
    Service
    )

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cars_active = Car.objects.filter(status="Active").values('mark', 'model', 'year', 'vin_code', 'status', 'license_plate')
        context['cars_active'] = cars_active
        context['form'] = AddCarForm()
        return context
    

class AddCarView(View):
    def post(self, request):
        form = AddCarForm(request.POST)

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


class OwnerCreateView(LoginRequiredMixin, CreateView):
    model=Owner
    form_class=OwnerForm
    template_name="owner/create.html"
    success_url="/core/owners/"


class OwnerListView(LoginRequiredMixin, ListView):
    model=Owner
    paginate_by=20
    template_name="owner/list.html"

    def get_queryset(self):
        owner_cars=(Owner.objects
                    .annotate(cars_count=Count("cars"))
                    .order_by("first_name", "last_name")
                    )
        return owner_cars            
    
# View for owner car list

class OwnerDetailView(LoginRequiredMixin, DetailView):
    model=Owner
    template_name="owner/detail.html"

class OwnerUpdateView(LoginRequiredMixin, UpdateView):
    model=Owner
    form_class=OwnerForm
    template_name="owner/update.html"
    success_url="/core/owners/"

class OwnerDeleteView(LoginRequiredMixin, DeleteView):
    model=Owner
    template_name="owner/owner_confirm_delete.html"
    success_url="/core/owners/"

class ServiceCreateView(LoginRequiredMixin, CreateView):
    model=Service
    form_class=ServiceForm
    template_name="service/create.html"
    success_url="/core/services/"

class ServiceDetailView(LoginRequiredMixin, DetailView):
    model=Service
    template_name="service/detail.html"

class ServiceDeleteView(LoginRequiredMixin, DeleteView):
    model=Service
    template_name="service/service_confirm_delete.html"
    success_url="core/services/"
class ServiceUpdateView(LoginRequiredMixin, UpdateView):
    model=Service
    form_class=ServiceForm
    template_name="service/update.html"
    success_url="/core/services/"

class ServiceListView(LoginRequiredMixin, ListView):
    model=Service
    template_name="service/list.html"
