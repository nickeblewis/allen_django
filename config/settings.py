"""
Settings for the Allen Family Accounting site.

Everything that differs between local Docker and Railway comes from the
environment. There's no database: the site is a single page plus a contact
form that sends an email.
"""

import os
import sys
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str) -> list[str]:
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]


DEBUG = env_bool("DEBUG")
TESTING = "pytest" in sys.modules

SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    if not (DEBUG or TESTING):
        raise ImproperlyConfigured("SECRET_KEY must be set when DEBUG is off.")
    SECRET_KEY = "dev-only-insecure-secret-key"

# Railway sets RAILWAY_PUBLIC_DOMAIN for the service's generated domain; a custom
# domain is added through ALLOWED_HOSTS.
RAILWAY_PUBLIC_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS")
if RAILWAY_PUBLIC_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)
# Railway's healthcheck calls from this host.
ALLOWED_HOSTS.append("healthcheck.railway.app")
ALLOWED_HOSTS.append("allendjango-production.up.railway.app")
if DEBUG or TESTING:
    ALLOWED_HOSTS += ["localhost", "127.0.0.1", "0.0.0.0", "[::1]", "testserver"]

CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
if RAILWAY_PUBLIC_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RAILWAY_PUBLIC_DOMAIN}")

INSTALLED_APPS = [
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django_tailwind_cli",
    "site_pages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "site_pages.context_processors.site",
            ],
        },
    },
]

# No database yet. Nothing here needs one: messages live in a cookie and the
# contact form only sends an email.
DATABASES = {}
MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True

# --- Static files -----------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# `public/` is served from the site root (favicon.ico, robots.txt).
WHITENOISE_ROOT = BASE_DIR / "public"

TAILWIND_CLI_SRC_CSS = "assets/css/source.css"
TAILWIND_CLI_DIST_CSS = "css/tailwind.css"
TAILWIND_CLI_VERSION = "4.1.11"
# The Docker image keeps the binary outside /app, so the compose bind mount
# doesn't hide it. Locally it goes in .django_tailwind_cli/.
TAILWIND_CLI_PATH = os.environ.get("TAILWIND_CLI_PATH") or None

STORAGES = {
    # Hashed, compressed file names in production. Dev and tests skip the
    # manifest, which only exists after `collectstatic`.
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        if DEBUG or TESTING
        else "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# --- Email (contact form) ---------------------------------------------------

CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "allenfamilybooks5@gmail.com")

_resend_api_key = os.environ.get("RESEND_API_KEY", "")
_email_host = os.environ.get("EMAIL_HOST", "")
if _resend_api_key:
    # Resend's HTTP API. Railway blocks outbound SMTP below the Pro plan.
    default_mailer = {
        "BACKEND": "anymail.backends.resend.EmailBackend",
        "OPTIONS": {"api_key": _resend_api_key},
    }
elif _email_host:
    default_mailer = {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": {
            "host": _email_host,
            "port": int(os.environ.get("EMAIL_PORT", "587")),
            "username": os.environ.get("EMAIL_HOST_USER", ""),
            "password": os.environ.get("EMAIL_HOST_PASSWORD", ""),
            "use_tls": env_bool("EMAIL_USE_TLS", True),
            "timeout": 10,
        },
    }
else:
    # Locally, emails are printed in the `docker compose` log.
    default_mailer = {"BACKEND": "django.core.mail.backends.console.EmailBackend"}

MAILERS = {"default": default_mailer}

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")
if not DEFAULT_FROM_EMAIL:
    if _resend_api_key:
        # Resend's shared test sender; it only delivers to the Resend account's
        # own address. Set DEFAULT_FROM_EMAIL once a domain is verified.
        DEFAULT_FROM_EMAIL = "Allen Family Accounting <onboarding@resend.dev>"
    else:
        DEFAULT_FROM_EMAIL = os.environ.get("EMAIL_HOST_USER") or CONTACT_EMAIL

# --- Security behind Railway's proxy ----------------------------------------

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SECURE_REDIRECT_EXEMPT = [r"^up$"]
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

# --- Site identity ------------------------------------------------------------

SITE = {
    "name": "Allen Family Accounting",
    "description": (
        "Professional, personal accounting services for individuals and businesses. "
        "Building financial confidence, one family at a time."
    ),
    "email": CONTACT_EMAIL,
}
