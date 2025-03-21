from .base import *

DEBUG = config("DEBUG", default=True, cast=bool)
SECRET_KEY = config("SECRET_KEY", default="dev-fallback-key")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=lambda v: v.split(','))

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

try:
    from .local import *
except ImportError:
    pass
