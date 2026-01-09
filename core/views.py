import logging
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, CreateView, ListView, View, TemplateView
from django.shortcuts import get_object_or_404
from django.db.models import Count
from .forms import AddCarForm, OwnerForm, ServiceForm, OutlayFrom
from .models import Car, Owner, CarPhoto, Service, Outlay
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from .mixins import RoleRequiredMixin
from django.shortcuts import render, redirect
from .services import create_car_with_photos, update_car_with_photos, delete_car, get_outlays, get_outlay, create_outlay, get_outlay_form_data, update_outlay, get_chat_list, get_chat_info

logger = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cars_active = Car.objects.filter(status="Active").select_related('owner')
        cars_pending = Car.objects.filter(status="Await").select_related('owner')
        context['cars_active'] = cars_active
        context['cars_pending'] = cars_pending
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
        # Get outlays for this car
        outlays = Outlay.objects.filter(cars=self.object).select_related('amount').order_by('-created_at', '-updated_at')
        context["outlays"] = outlays
        
        # Calculate total outlay amount
        total = 0
        for outlay in outlays:
            if outlay.amount.full_price:
                total += float(outlay.amount.full_price)
            elif outlay.amount.price_per_item and outlay.amount.item_count:
                total += float(outlay.amount.price_per_item) * int(outlay.amount.item_count)
        context["outlays_total"] = total
        
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
            return JsonResponse({
                "status": "ok",
                "id": str(owner.uuid),
                "message": "Owner successfully updated!"
            })

        return JsonResponse({
            "status": "error",
            "errors": form.errors
        }, status=400)


class OwnerDetailView(LoginRequiredMixin, DetailView):
    model = Owner
    template_name = "owner/detail.html"


class OwnerDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            owner = Owner.objects.get(uuid=pk)
            owner.delete()
            return JsonResponse({
                "status": "ok",
                "message": "Owner successfully deleted!",
            })
        except Owner.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "errors": {"__all__": ["Owner not found"]},
            }, status=404)


class ServiceListView(LoginRequiredMixin, ListView):
    model = Service
    template_name = "service/list.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ServiceForm()
        return context


class ServiceCreateView(LoginRequiredMixin, View):
    def post(self, request):
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save()
            return JsonResponse({
                "status": "ok",
                "id": str(service.uuid),
                "message": "Service successfully added!",
            })
        return JsonResponse({
            "status": "error",
            "errors": form.errors,
        }, status=400)


class ServiceUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            service = Service.objects.get(uuid=pk)
        except Service.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "errors": {"__all__": ["Service not found"]},
            }, status=404)
        
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            service = form.save()
            return JsonResponse({
                "status": "ok",
                "id": str(service.uuid),
                "message": "Service successfully updated!",
            })
        return JsonResponse({
            "status": "error",
            "errors": form.errors,
        }, status=400)


class ServiceDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            service = Service.objects.get(uuid=pk)
            service.delete()
            return JsonResponse({
                "status": "ok",
                "message": "Service successfully deleted!",
            })
        except Service.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "errors": {"__all__": ["Service not found"]},
            }, status=404)


class ServiceDetailView(LoginRequiredMixin, DetailView):
    model = Service
    template_name = "service/detail.html"


class OutlayView(LoginRequiredMixin, View):
    template_name = "outlay.html"

    def get(self, request):
        # Get filter parameter
        filter_type = request.GET.get('type', 'all')  # all, service, other
        filter_category = request.GET.get('category', 'all')  # all, fuel, parts, documents, another
        
        # Get all outlays
        outlays_qs = Outlay.objects.select_related('amount').prefetch_related('cars').order_by('-created_at', '-updated_at')
        
        # Apply type filter
        if filter_type == 'service':
            outlays_qs = outlays_qs.filter(type='service')
        elif filter_type == 'other':
            outlays_qs = outlays_qs.filter(type='other')
        
        # Apply category filter
        if filter_category != 'all':
            outlays_qs = outlays_qs.filter(category=filter_category)
        
        # Convert to list of dicts for template compatibility
        outlays = []
        for outlay in outlays_qs:
            cars_list = list(outlay.cars.all())
            if cars_list:
                for car in cars_list:
                    outlays.append({
                        'uuid': outlay.uuid,
                        'type': outlay.type,
                        'category': outlay.category,
                        'category_name': outlay.category_name,
                        'service_name': outlay.service_name,
                        'name': outlay.name,
                        'comment': outlay.comment,
                        'description': outlay.description,  # For backward compatibility
                        'created_at': outlay.created_at,
                        'updated_at': outlay.updated_at,
                        'cars__mark': car.mark,
                        'cars__model': car.model,
                        'cars__license_plate': car.license_plate,
                        'amount__price_per_item': outlay.amount.price_per_item,
                        'amount__item_count': outlay.amount.item_count,
                        'amount__full_price': outlay.amount.full_price,
                    })
            else:
                # If no cars associated, still show the outlay
                outlays.append({
                    'uuid': outlay.uuid,
                    'type': outlay.type,
                    'category': outlay.category,
                    'category_name': outlay.category_name,
                    'service_name': outlay.service_name,
                    'name': outlay.name,
                    'comment': outlay.comment,
                    'description': outlay.description,  # For backward compatibility
                    'created_at': outlay.created_at,
                    'updated_at': outlay.updated_at,
                    'cars__mark': '',
                    'cars__model': '',
                    'cars__license_plate': '',
                    'amount__price_per_item': outlay.amount.price_per_item,
                    'amount__item_count': outlay.amount.item_count,
                    'amount__full_price': outlay.amount.full_price,
                })
        
        context = {
            "outlays": outlays,
            "form": OutlayFrom(),
            "filter_type": filter_type,
            "filter_category": filter_category,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = OutlayFrom(request.POST)
        
        # Check if car field has value even if form is not valid
        car_value = request.POST.get('car')
        if not car_value:
            form.add_error('car', 'Оберіть автомобіль')
        
        if not form.is_valid():
            # If form is invalid, render with errors
            filter_type = request.GET.get('type', 'all')
            filter_category = request.GET.get('category', 'all')
            outlays_qs = Outlay.objects.select_related('amount').prefetch_related('cars').order_by('-created_at', '-updated_at')
            
            if filter_type == 'service':
                outlays_qs = outlays_qs.filter(type='service')
            elif filter_type == 'other':
                outlays_qs = outlays_qs.filter(type='other')
            
            if filter_category != 'all':
                outlays_qs = outlays_qs.filter(category=filter_category)
            
            outlays = []
            for outlay in outlays_qs:
                cars_list = list(outlay.cars.all())
                if cars_list:
                    for car in cars_list:
                        outlays.append({
                            'uuid': outlay.uuid,
                            'type': outlay.type,
                            'category': outlay.category,
                            'category_name': outlay.category_name,
                            'service_name': outlay.service_name,
                            'name': outlay.name,
                            'comment': outlay.comment,
                            'description': outlay.description,
                            'created_at': outlay.created_at,
                            'updated_at': outlay.updated_at,
                            'cars__mark': car.mark,
                            'cars__model': car.model,
                            'cars__license_plate': car.license_plate,
                            'amount__price_per_item': outlay.amount.price_per_item,
                            'amount__item_count': outlay.amount.item_count,
                            'amount__full_price': outlay.amount.full_price,
                        })
            
            context = {
                "outlays": outlays,
                "form": form,
                "filter_type": filter_type,
                "filter_category": filter_category,
            }
            return render(request, self.template_name, context)
        
        cd = form.cleaned_data
        
        # Validate name for service type
        if cd['service_type'] == 'service' and not cd.get('name'):
            form.add_error('name', 'Назва витрати обов\'язкова для типу "Сервіс"')
            filter_type = request.GET.get('type', 'all')
            filter_category = request.GET.get('category', 'all')
            outlays_qs = Outlay.objects.select_related('amount').prefetch_related('cars').order_by('-created_at', '-updated_at')
            
            if filter_type == 'service':
                outlays_qs = outlays_qs.filter(type='service')
            elif filter_type == 'other':
                outlays_qs = outlays_qs.filter(type='other')
            
            if filter_category != 'all':
                outlays_qs = outlays_qs.filter(category=filter_category)
            
            outlays = []
            for outlay in outlays_qs:
                cars_list = list(outlay.cars.all())
                if cars_list:
                    for car in cars_list:
                        outlays.append({
                            'uuid': outlay.uuid,
                            'type': outlay.type,
                            'category': outlay.category,
                            'category_name': outlay.category_name,
                            'service_name': outlay.service_name,
                            'name': outlay.name,
                            'comment': outlay.comment,
                            'description': outlay.description,
                            'created_at': outlay.created_at,
                            'updated_at': outlay.updated_at,
                            'cars__mark': car.mark,
                            'cars__model': car.model,
                            'cars__license_plate': car.license_plate,
                            'amount__price_per_item': outlay.amount.price_per_item,
                            'amount__item_count': outlay.amount.item_count,
                            'amount__full_price': outlay.amount.full_price,
                        })
            
            context = {
                "outlays": outlays,
                "form": form,
                "filter_type": filter_type,
                "filter_category": filter_category,
            }
            return render(request, self.template_name, context)
        
        # Create outlay using service function
        outlay = create_outlay(
            type=cd['service_type'],
            name=cd.get('name', ''),
            car=cd['car'],  # Single car instead of list
            price_per_item=cd.get('price_per_item') or 0,
            item_count=cd.get('item_count') or 0,
            created_at=cd['date'],
            full_price=cd.get('full_price'),
            category=cd.get('category'),
            category_name=cd.get('category_name'),
            service_name=cd.get('service_name'),
            comment=cd.get('comment'),
            description=cd.get('description'),  # For backward compatibility
        )
        
        return redirect('outlay')


class OutlatDetailView(LoginRequiredMixin, View):
    template_name = "outlay_detail.html"

    def get(self, request, pk):
        outlay = get_outlay(pk)
        form = get_outlay_form_data(pk)
        context = {
            "outlay": outlay,
            "outlay_uuid": pk,
            "form": form,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        try:
            outlay = get_outlay(pk)
        except Outlay.DoesNotExist:
            return redirect('outlay')
        
        form = OutlayFrom(request.POST)
        
        # Check if car field has value even if form is not valid
        car_value = request.POST.get('car')
        if not car_value:
            form.add_error('car', 'Оберіть автомобіль')
        
        if form.is_valid():
            cd = form.cleaned_data
            
            # Validate name for service type
            if cd['service_type'] == 'service' and not cd.get('name'):
                form.add_error('name', 'Назва витрати обов\'язкова для типу "Сервіс"')
                context = {
                    "outlay": outlay,
                    "outlay_uuid": pk,
                    "form": form,
                }
                return render(request, self.template_name, context)
            
            # Validate car is selected
            if not cd.get('car'):
                form.add_error('car', 'Оберіть автомобіль')
                context = {
                    "outlay": outlay,
                    "outlay_uuid": pk,
                    "form": form,
                }
                return render(request, self.template_name, context)
            
            try:
                # Update outlay using service function
                update_outlay(pk, form)
                
                # Get car UUID for redirect
                updated_outlay = get_outlay(pk)
                cars = list(updated_outlay.cars.all())
                car_uuid = cars[0].uuid if cars else None
                
                # Check if request is from car detail page
                referer = request.META.get('HTTP_REFERER', '')
                if car_uuid and '/core/cars/' in referer:
                    return redirect('car-detail', pk=car_uuid)
                
                return redirect('outlay')
            except Exception as e:
                logger.error(f"Error updating outlay {pk}: {str(e)}")
                form.add_error(None, f'Помилка оновлення витрати: {str(e)}')
                context = {
                    "outlay": outlay,
                    "outlay_uuid": pk,
                    "form": form,
                }
                return render(request, self.template_name, context)
        else:
            # Form is invalid, render with errors
            context = {
                "outlay": outlay,
                "outlay_uuid": pk,
                "form": form,
            }
            return render(request, self.template_name, context)


class OutlayDeleteView(LoginRequiredMixin, View):
    def get(self, request):
        raise Http404("Page not found")
    def post(self, request, pk):
        try:
            outlay = Outlay.objects.get(uuid=pk)
            # Get car UUID before deleting (if any) - support both ManyToMany and ForeignKey
            car_uuid = None
            if hasattr(outlay, 'car') and outlay.car:
                car_uuid = outlay.car.uuid
            else:
                cars = list(outlay.cars.all())
                car_uuid = cars[0].uuid if cars else None
            
            outlay.delete()
            
            # Check if it's an AJAX request (no validation needed for delete)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    "status": "ok",
                    "message": "Витрату успішно видалено",
                })
            
            # Check if request is from car detail page or if we have car UUID
            referer = request.META.get('HTTP_REFERER', '')
            if car_uuid or '/core/cars/' in referer:
                # Extract car UUID from referer or use the one from outlay
                if not car_uuid:
                    import re
                    match = re.search(r'/core/cars/([0-9a-f-]+)', referer)
                    if match:
                        car_uuid = match.group(1)
                
                if car_uuid:
                    return redirect('car-detail', pk=car_uuid)
            
            return redirect('outlay')
        except Outlay.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    "status": "error",
                    "errors": {"__all__": ["Витрату не знайдено"]},
                }, status=404)
            return redirect('outlay')
        except Exception as e:
            logger.error(f"Error deleting outlay {pk}: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    "status": "error",
                    "errors": {"__all__": [f"Помилка видалення: {str(e)}"]},
                }, status=500)
            return redirect('outlay')


class ChatView(LoginRequiredMixin, View):
    template_name = "chat/chat.html"

    def get(self, request):
        context = {'chats': get_chat_list()}
        return render(request, self.template_name, context)


    def post(self, request, new_chat_id):
        pass


class ChatDetailView(LoginRequiredMixin, View):
    template_name = "chat/chat_detail.html"

    def get(self, request, chat_id):
        context = {"chat": get_chat_info(chat_id)}
        return render(request, self.template_name, context)

from .analitics import AnalysManager 

class AnaliticsView(LoginRequiredMixin, View):
    template_name = ""

    def get(self, request):
        test_car = Car.objects.all().last()
        t = AnalysManager(test_car)
        t.test()
        return JsonResponse({"ok": "ok"})


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
