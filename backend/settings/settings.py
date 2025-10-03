import os
import sys
import logging

import structlog
from structlog import contextvars
from structlog.stdlib import ProcessorFormatter, add_logger_name
from structlog.processors import (
    TimeStamper,
    add_log_level,
    format_exc_info,
    JSONRenderer,
)
from structlog.dev import ConsoleRenderer
from pathlib import Path

import dj_database_url

from settings.core import get_env_param_bool, get_env_param_str, get_env_param_list

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent


SECRET_KEY = get_env_param_str("SECRET_KEY", "dev")
DEBUG = get_env_param_bool("DEBUG", False)

foreign_pre_chain = [
    structlog.contextvars.merge_contextvars,
    add_log_level,
    TimeStamper(fmt="iso", utc=True),
    format_exc_info,
]

if not DEBUG:
    renderer = JSONRenderer()
    root_level = "INFO"
else:
    renderer = ConsoleRenderer(colors=True)
    root_level = "DEBUG"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "struct": {
            "()": ProcessorFormatter,
            "processor": renderer,
            "foreign_pre_chain": foreign_pre_chain,
        },
    },
    "handlers": {
        "default": {
            "level": root_level,
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "struct",
        },
    },
    "root": {
        "handlers": ["default"],
        "level": root_level,
    },
    "loggers": {
        "django": {"handlers": ["default"], "level": root_level, "propagate": False},
        "django.db.backends": {"handlers": ["default"], "level": "WARNING", "propagate": False},
        "django.template": {"handlers": ["default"], "level": "WARNING", "propagate": False},
        "asgiref": {"handlers": ["default"], "level": "WARNING", "propagate": False},
        "django.request": {"handlers": ["default"], "level": "ERROR", "propagate": False},
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["default"], "level": "WARN", "propagate": False},
        "channels": {"handlers": ["default"], "level": "INFO", "propagate": False},
    },
}

structlog.configure(
    processors=[
        add_logger_name,
        contextvars.merge_contextvars,
        add_log_level,
        TimeStamper(fmt="iso"),
        format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

ALLOWED_HOSTS = get_env_param_list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])
CSRF_TRUSTED_ORIGINS = get_env_param_list("CSRF_TRUSTED_ORIGINS", default=[])

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
    "votings",
    "ws"
]

INSTALLED_APPS = DJANGO_APPS + THIRD_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "api.middleware.AccessLogMiddleware",
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

REDIS_PASSWORD = get_env_param_str("REDIS_PASSWORD", raise_exception=False)

if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@watchy-redis:6379/0"
else:
    REDIS_URL = f"redis://watchy-redis:6379/0"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "DECODE_RESPONSES": True,
        }
    }
}

CORS_ALLOWED_ORIGINS = get_env_param_list("CORS_ALLOWED_ORIGINS", default=["127.0.0.1:3000", "localhost:3000"])

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    'DEFAULT_AUTHENTICATION_CLASSES': [
        "rest_framework.authentication.BasicAuthentication",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Watchy API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS": {
        "displayOperationId": True,
    },
}


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
