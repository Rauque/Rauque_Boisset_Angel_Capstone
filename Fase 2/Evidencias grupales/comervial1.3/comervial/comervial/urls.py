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
    path("pagos/", include("payments.urls")),

    # --- SECCIÓN DE RESETEO DE CONTRASEÑA (INICIO) ---
    # Es vital poner esto ANTES del include de auth.urls y usar 'accounts/' al principio

    # 1. Formulario para pedir el correo
    path('accounts/password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), 
         name='password_reset'),

    # 2. Mensaje de "Te hemos enviado un correo"
    path('accounts/password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), 
         name='password_reset_done'),

    # 3. Link que llega al email para poner la nueva clave (fíjate en los parámetros <uidb64> y <token>)
    path('accounts/reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), 
         name='password_reset_confirm'),

    # 4. Mensaje de "Contraseña cambiada con éxito"
    path('accounts/reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), 
         name='password_reset_complete'),
    # --- SECCIÓN DE RESETEO DE CONTRASEÑA (FIN) ---


    # Rutas predeterminadas (Login/Logout estándar)
    path("accounts/", include("django.contrib.auth.urls")),
    
    # Tus otras URLs de cuentas
    path("accounts/", include("apps.accounts.urls")),
]

admin.site.site_header = "Comervial — Administración"
admin.site.site_title = "Comervial Admin"
admin.site.index_title = "Panel de control"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
