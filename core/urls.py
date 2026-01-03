from django.urls import path
from django.views.generic import RedirectView
from . import views as view

urlpatterns = [
    path("", RedirectView.as_view(url="/core/cars", permanent=False), name="core-index"),
    path("cars", view.DashboardView.as_view(), name="cars"),
    path("cars/create/", view.AddCarView.as_view(), name="add_car_ajax"),
    path("cars/<uuid:pk>/", view.CarDetailView.as_view(), name="car-detail"),
    path("cars/update/<uuid:pk>/", view.CarUpdateView.as_view(), name="car-update"),
    path("cars/delete/<uuid:pk>/", view.CarDeleteView.as_view(), name="car-delete"),
    path("owners/", view.OwnerListView.as_view(), name="owner-list"),
    path("owners/<uuid:pk>/", view.OwnerDetailView.as_view(), name="owner-detail"),
    path("owners/create/", view.OwnerCreateView.as_view(), name="owner-create"),
    path("owners/update/<uuid:pk>/", view.OwnerUpdateView.as_view(), name="owner-update"),
    path("owners/delete/<uuid:pk>/", view.OwnerDeleteView.as_view(), name="owner-delete"),
    path("services/", view.ServiceListView.as_view(), name="service-list"),
    path("services/create/", view.ServiceCreateView.as_view(), name="service-create"),
    path("services/update/<uuid:pk>/", view.ServiceUpdateView.as_view(), name="service-update"),
    path("services/delete/<uuid:pk>/", view.ServiceDeleteView.as_view(), name="service-delete"),
    path("services/<uuid:pk>/", view.ServiceDetailView.as_view(), name="service-detail"),
    path("outlay/", view.OutlayView.as_view(), name="outlay"),
    path("outlay/<uuid:pk>/", view.OutlatDetailView.as_view(), name="outlay_detail"),
    path("outlay/<uuid:pk>/delete", view.OutlayDeleteView.as_view(), name="outlay_delete"),
    path("car-service-plan/create/", view.CarServiceCreate.as_view(), name="car-service-plan-create"),
]
