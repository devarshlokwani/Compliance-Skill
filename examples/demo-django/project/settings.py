import os

import sentry_sdk

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = False
ALLOWED_HOSTS = ["meetingnotes.example"]

STRIPE_SECRET_KEY = os.environ["STRIPE_SECRET_KEY"]

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    # Attaches request bodies and user identifiers to every event.
    send_default_pii=True,
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "subscriptions",
]

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [os.path.join(BASE_DIR, "templates")],
    "APP_DIRS": True,
}]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DATABASE_NAME"],
    }
}
