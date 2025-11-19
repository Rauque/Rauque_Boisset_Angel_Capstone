# comervial/comervial/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("panel/", admin.site.urls),
    path("", include("apps.pages.urls")),
    path("cotizador/", include("apps.quotes.urls")),
    path("catalogo/", include("apps.catalog.urls")),

    # Flow / pagos
    path("pagos/", include("payments.urls")),

    # Autenticación
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("apps.accounts.urls")),
]

admin.site.site_header = "Comervial — Administración"
admin.site.site_title = "Comervial Admin"
admin.site.index_title = "Panel de control"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
