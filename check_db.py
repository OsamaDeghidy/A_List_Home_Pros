import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alistpros.settings')
django.setup()

from django.conf import settings

print("Database Configuration:")
print("-" * 30)
print(f"ENGINE: {settings.DATABASES['default']['ENGINE']}")
for key, value in settings.DATABASES['default'].items():
    if key != 'OPTIONS':
        print(f"{key}: {value}")
    else:
        print(f"{key}:")
        for opt_key, opt_val in value.items():
            print(f"  {opt_key}: {opt_val}")

print("\nEnvironment Variables:")
print("-" * 30)
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'Not set')}")
