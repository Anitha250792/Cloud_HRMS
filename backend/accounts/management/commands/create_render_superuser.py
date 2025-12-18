from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Command(BaseCommand):
    help = "Create superuser on Render"

    def handle(self, *args, **kwargs):
        email = os.getenv("SUPERUSER_EMAIL")
        password = os.getenv("SUPERUSER_PASSWORD")

        if not email or not password:
            self.stdout.write("Superuser env vars not set")
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write("Superuser already exists")
            return

        User.objects.create_superuser(
            email=email,
            password=password,
            name="Admin"
        )

        self.stdout.write("✅ Superuser created successfully")
