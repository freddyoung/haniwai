from .base import *
import dj_database_url
import os

# ✅ Installed Apps
INSTALLED_APPS += [
    'cloudinary',
    'cloudinary_storage',
]

# ✅ Cloudinary Storage Config
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
    'SECURE': True,
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# ✅ Whitenoise for static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MIDDLEWARE += ["whitenoise.middleware.WhiteNoiseMiddleware"]

# ✅ Environment Variables
DEBUG = os.getenv("DEBUG", "False") == "True"

SECRET_KEY = os.getenv("SECRET_KEY")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# ✅ Database
DATABASES = {
    "default": dj_database_url.config(default=os.getenv("DATABASE_URL"))
}

# ✅ Static & Media
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# ✅ Security settings
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

# ✅ Optional email backend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
