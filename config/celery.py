import os

from celery import Celery

# Tell Celery which Django settings module to use.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Create the Celery application.
app = Celery("anime_project")

# Load Celery settings from Django settings.py.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Automatically discover tasks.py files in installed Django apps.
app.autodiscover_tasks()