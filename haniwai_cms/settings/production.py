from .base import *
import dj_database_url

DEBUG = config("DEBUG", default=False, cast=bool)

SECRET_KEY = config("SECRET_KEY")

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=lambda v: v.split(','))

# Database
DATABASES = {
    "default": dj_database_url.config(default=config("DATABASE_URL"))
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Security settings
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

# Whitenoise for static files
MIDDLEWARE += ["whitenoise.middleware.WhiteNoiseMiddleware"]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Email (Optional, can be improved later)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Optional: Disable Django debug toolbar or any dev-only middleware
