import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evento_qr.settings_production')
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@ejemplo.com', 'admin123')
    print("Superusuario creado: admin / admin123")
else:
    print("El superusuario ya existe")