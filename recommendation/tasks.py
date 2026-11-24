from celery import shared_task
from django.conf import settings
from django.utils.module_loading import import_string


@shared_task
def send_log_notification(message):
    client_class = import_string(settings.LOGGER_CLIENT)
    client = client_class()

    return client.send_message(message)
