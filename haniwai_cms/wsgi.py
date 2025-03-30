"""
WSGI config for haniwai_cms project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haniwai_cms.settings.production")

application = get_wsgi_application()

from django.contrib.auth import get_user_model

if os.environ.get("CREATE_SUPERUSER", "false") == "true":
    try:
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                "admin", "fmyoung96@gmail.com", "3981haniwai"
            )
            print("✅ Superuser created successfully!")
    except Exception as e:
        print(f"Superuser creation failed: {e}")
