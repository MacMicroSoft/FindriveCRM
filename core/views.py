from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, CreateView, ListView, View, TemplateView
from django.shortcuts import get_object_or_404
from .forms import CarForm, OwnerForm
from .models import Car, Owner
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from .mixins import RoleRequiredMixin


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

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
