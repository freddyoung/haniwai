from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Creates an initial superuser if none exist"

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "adminpassword")
            self.stdout.write(self.style.SUCCESS("🟢 Superuser created: admin / adminpassword"))
        else:
            self.stdout.write(self.style.WARNING("🟡 Superuser already exists"))
