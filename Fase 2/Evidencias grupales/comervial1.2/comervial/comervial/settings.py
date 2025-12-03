import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.getenv("DEBUG", "False") == "True"
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

INSTALLED_APPS = [
    "payments",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Tus apps
    "apps.pages",
    "apps.quotes",
    "apps.accounts",   
    "apps.catalog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "comervial.urls"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ],
    },
}]

WSGI_APPLICATION = "comervial.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {"init_command": "SET sql_mode='STRICT_TRANS_TABLES'"},
    }
}

LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# === Email (Gmail SMTP) ===
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "comervial.hr@gmail.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")  # contraseña de aplicación
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "20"))

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "Comervial <comervial.hr@gmail.com>")
COTIZADOR_TO = os.getenv("COTIZADOR_TO", "comervial.hr@gmail.com")

EMAIL_SUBJECT_PREFIX = "[Comervial] "
SERVER_EMAIL = "Comervial <comervial.hr@gmail.com>"



DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Auth redirects
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "index"
LOGOUT_REDIRECT_URL = "index"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


MP_PUBLIC_KEY   = os.getenv("MP_PUBLIC_KEY", "TEST-APP_USR-269590d6-df27-4103-88c3-3166bb3fa41f")
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN", "TEST-APP_USR-7566504184875425-111114-5ff12051d688884be48e83cb9a0260e7-2982510326")
MP_SUCCESS_URL  = os.getenv("MP_SUCCESS_URL",  "http://127.0.0.1:8000/catalogo/pago/exito/")
MP_FAILURE_URL  = os.getenv("MP_FAILURE_URL",  "http://127.0.0.1:8000/catalogo/pago/error/")
MP_PENDING_URL  = os.getenv("MP_PENDING_URL",  "http://127.0.0.1:8000/catalogo/pago/pendiente/")
MP_WEBHOOK_URL  = os.getenv("MP_WEBHOOK_URL",  "http://127.0.0.1:8000/catalogo/pago/webhook/")

FLOW_API_KEY     = os.getenv("FLOW_API_KEY", "3ACF739C-C523-45AA-A5B5-5E7D6L3BFC29")
FLOW_SECRET_KEY  = os.getenv("FLOW_SECRET_KEY", "386473ac583e7d7ed49363983c451996dea9869a")
FLOW_API_URL     = os.getenv("FLOW_API_URL", "https://sandbox.flow.cl/api")
FLOW_RETURN_URL  = os.getenv("FLOW_RETURN_URL", "http://127.0.0.1:8000/pagos/flow/return/")
FLOW_CONFIRM_URL = os.getenv("FLOW_CONFIRM_URL", "http://127.0.0.1:8000/pagos/flow/confirm/")

CSRF_TRUSTED_ORIGINS = [
    "https://sandbox.flow.cl",
    "https://www.flow.cl",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]
