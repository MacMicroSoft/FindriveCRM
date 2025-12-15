"""
URL configuration for findrive_crm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

# Handle OPTIONS requests for non-existent API endpoints (from extensions/browsers)
@require_http_methods(["OPTIONS"])
def handle_options(request):
    response = HttpResponse()
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response["Access-Control-Max-Age"] = "86400"
    return response

urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),
    path("core/", include("core.urls")),
    path("", RedirectView.as_view(url="/core/cars", permanent=True)),
    path("accounts/", include("allauth.urls")),
    path("admin/", admin.site.urls),
    # Handle OPTIONS requests for API endpoints that don't exist (from extensions)
    path("api/v1/users/refresh/", handle_options, name="api-options-handler"),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
