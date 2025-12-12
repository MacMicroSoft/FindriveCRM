from django.urls import path
from . import views as view

urlpatterns = [
    path("", view.DashboardView.as_view(), name="dashboard"),
    path("cars/create/", view.AddCarView.as_view(), name="add_car_ajax"),
    # path("cars/<uuid:pk>/", view.CarDetailView.as_view(), name="car_detail"),
    # path("owner/create/", view.CreateOwnerView.as_view(), name="owner_create"),
    # path("cars/", view.CarListView.as_view(), name="car_list"),
    # path("owner/create/ajax/", view.OwnerCreateAjaxView.as_view(), name="owner_create_ajax"),
    # path("owners/", view.OwnerListView.as_view(), name="owner_list"),
    # path("invoices/", view.TemplateView.as_view(template_name="invoices/placeholder.html"), name="invoices"),
    # path("settings/", view.TemplateView.as_view(template_name="settings.html"), name="settings"),
    # path("notifications/", view.NotificationsView.as_view(), name="notifications"),
    # path("chat/", view.ChatView.as_view(), name="chat"),
]
