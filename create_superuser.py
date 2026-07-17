import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ictsystem.settings")
django.setup()

from django.contrib.auth.models import User
from assets.models import UserProfile

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")

if username and password:
    if User.objects.filter(username=username).exists():
        # User exists — reset password to make sure it matches env var
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f"Password reset for existing user: {username}")
    else:
        # Create fresh superuser
        user = User.objects.create_superuser(username, email, password)
        print(f"Superuser created: {username}")

    # Ensure profile exists
    UserProfile.objects.get_or_create(user=user)
    print("Profile confirmed.")
else:
    print("No username/password env vars found — skipping.")