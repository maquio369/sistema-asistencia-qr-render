# Usar Python 3.11 como imagen base
FROM python:3.11-slim

# Configurar variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=evento_qr.settings_docker

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código del proyecto
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/media/fotos_invitados /app/media/qr_codes /app/staticfiles

# Configurar permisos
RUN chmod -R 755 /app/media /app/staticfiles

# Exponer el puerto
EXPOSE 8000

# Script de inicio
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 evento_qr.wsgi:application"]
