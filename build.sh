#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Iniciando build para Render..."

pip install -r requirements.txt

echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --no-input

echo "🗄️ Aplicando migraciones..."
python manage.py migrate

echo "✅ Build completado exitosamente!"