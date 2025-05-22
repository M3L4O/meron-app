#!/bin/sh

run_and_prefix() {
  name=$1
  shift
  "$@" 2>&1 | while IFS= read -r line; do
    echo "[$name] $line"
  done
}

echo "Database Startup"
echo "====================="
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
echo "====================="

echo "Iniciando Django..."
run_and_prefix "Django" python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

sleep 5

echo "Iniciando Celery Worker..."
run_and_prefix "Celery Worker" celery -A database worker -l info &
CELERY_WORKER_PID=$!

echo "Iniciando Celery Beat..."
run_and_prefix "Celery Beat" celery -A database beat -l info &
CELERY_BEAT_PID=$!

# Espera todos os processos
wait $DJANGO_PID $CELERY_WORKER_PID $CELERY_BEAT_PID
