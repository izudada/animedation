
import logging

from django.conf import settings
from django.utils.module_loading import import_string


class CustomLogging:

    @classmethod
    def _get_client(cls):
        client_class = import_string(settings.LOGGER_CLIENT)
        return client_class()

    @classmethod
    def error(cls, message, extra=None, payload=None, send_notification=True):
        logging.error(message, extra={"context": extra, "payload": payload})

        if send_notification:
            client = cls._get_client()
            client.send_message(
                message=f"ERROR: {message}\nExtra: {extra}\nPayload: {payload}"
            )

    @classmethod
    def warning(cls, message, extra=None, send_notification=False):
        logging.warning(message, extra={"context": extra})

        if send_notification:
            client = cls._get_client()
            client.send_message(
                message=f"WARNING: {message}\nExtra: {extra}"
            )

    @classmethod
    def info(cls, message, extra=None, send_notification=False):
        logging.info(message, extra={"context": extra})

        if send_notification:
            client = cls._get_client()
            client.send_message(
                message=f"INFO: {message}\nExtra: {extra}"
            )

    @classmethod
    def critical(cls, message, extra=None, payload=None, send_notification=True):
        logging.critical(
            message,
            extra={"context": extra, "payload": payload},
        )

        if send_notification:
            client = cls._get_client()
            client.send_message(
                message=f"CRITICAL: {message}\nExtra: {extra}\nPayload: {payload}"
            )
