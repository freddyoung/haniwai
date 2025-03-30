from .base import *
import dj_database_url

INSTALLED_APPS += [
    'cloudinary',
    'cloudinary_storage',
]

# Cloudinary Storage Settings
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files (not needed because Cloudinary manages them)
MEDIA_URL = ""

# Database
DATABASES = {
    "default": dj_database_url.config(default=os.getenv("DATABASE_URL"))
}

DEBUG = False
SECRET_KEY = os.getenv("SECRET_KEY")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", default="*").split(",")

MIDDLEWARE += ["whitenoise.middleware.WhiteNoiseMiddleware"]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
