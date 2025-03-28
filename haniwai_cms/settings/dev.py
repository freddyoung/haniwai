from .base import *
from decouple import Config, RepositoryEnv
config = Config(RepositoryEnv('.env.dev'))

# ✅ Get secret key, debug, and allowed hosts from .env.dev
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool, default=True)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=lambda v: v.split(","))

# ✅ Email backend just for local dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ✅ Static file storage (optional for local dev, but useful)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

try:
    from .local import *
except ImportError:
    pass
