from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("panel/", admin.site.urls),
    path("", include("apps.pages.urls")),
    path("cotizador/", include("apps.quotes.urls")),
    path("catalogo/", include("apps.catalog.urls")),

    # Flow / pagos
    path("pagos/", include("payments.urls")),

    # Autenticación
    # Ruta personalizada para restablecimiento de contraseña
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),

    # Rutas predeterminadas de autenticación (debe ir después de la ruta personalizada)
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("apps.accounts.urls")),
]

admin.site.site_header = "Comervial — Administración"
admin.site.site_title = "Comervial Admin"
admin.site.index_title = "Panel de control"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
