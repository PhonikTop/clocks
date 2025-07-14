import os
import sys
from pathlib import Path

import dj_database_url

from settings.core import get_env_param_bool, get_env_param_str

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent


def at_project_root(name):
    return os.path.normpath(os.path.join(PROJECT_ROOT, name))

def get_list(key, default=None):
    val = os.getenv(key)
    return [v.strip() for v in val.split(",")] if val else default or []

sys.path.insert(1, PROJECT_ROOT)
for app_lookup_path in ("clocks",):
    sys.path.insert(1, at_project_root(app_lookup_path))

SECRET_KEY = get_env_param_str("SECRET_KEY", "dev")
DEBUG = get_env_param_bool("DEBUG", False)

ALLOWED_HOSTS = get_list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])
CSRF_TRUSTED_ORIGINS = get_list("CSRF_TRUSTED_ORIGINS", default=[])

# Application definition
DJANGO_APPS = [
    "django.contrib.contenttypes",
    "grappelli",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_APPS = [
    "channels",
    "rest_framework",
    "corsheaders",
    "drf_spectacular"
]

LOCAL_APPS = [
    "rooms",
    "users",
    "meetings",
    "ws"
]

INSTALLED_APPS = DJANGO_APPS + THIRD_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "settings.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "settings.wsgi.application"
ASGI_APPLICATION = "settings.asgi.application"

DATABASES = {}
DATABASES["default"] = db = dj_database_url.parse(get_env_param_str("DATABASE_URL"))

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 60 * 60 * 5


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("watchy-redis", 6379)],
        },
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://watchy-redis:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "DECODE_RESPONSES": True,
        }
    }
}

CORS_ALLOWED_ORIGINS = get_list("CORS_ALLOWED_ORIGINS", default=["127.0.0.1:3000", "localhost:3000"])

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Watchy API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
