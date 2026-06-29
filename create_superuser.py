import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "digital_hub.settings")
django.setup()

from django.contrib.auth.models import User

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print("Superuser created")
else:
    print("Superuser already exists")


  

