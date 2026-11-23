
from django.conf import settings

from .base_api_client import BaseAPIClient


class TelegramClient(BaseAPIClient):
    """Client for interacting with the Telegram Bot API."""

    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID

        super().__init__(
            base_url=f"https://api.telegram.org/bot{self.token}",
            timeout=10,
        )

    def get_me(self):
        """
        Retrieve information about the Telegram bot.

        Sample response:
        {
            "ok": True,
            "result": {
                "id": 2091040099,
                "is_bot": True,
                "first_name": "Anime Monitor",
                "username": "anime_monitor_bot"
            }
        }
        """
        return self._initiate_request(
            endpoint="getMe",
            method="GET",
        )

    def get_updates(self, offset=None, timeout=10):
        """
        Retrieve incoming updates (messages, commands, etc.) sent to the bot.

        Args:
            offset (int, optional): Identifier of the first update to retrieve.
            timeout (int): Long-polling timeout in seconds.

        Sample response:
        {
            "ok": True,
            "result": [
                {
                    "update_id": 123456789,
                    "message": {
                        "message_id": 10,
                        "chat": {
                            "id": 123456789,
                            "type": "private"
                        },
                        "text": "Hello"
                    }
                }
            ]
        }
        """
        params = {"timeout": timeout}

        if offset is not None:
            params["offset"] = offset

        return self._initiate_request(
            endpoint="getUpdates",
            method="GET",
            params=params,
        )

    def get_webhook_info(self):
        """
        Retrieve information about the bot's current webhook configuration.

        Sample response:
        {
            "ok": True,
            "result": {
                "url": "https://example.com/telegram/webhook/",
                "has_custom_certificate": False,
                "pending_update_count": 0
            }
        }
        """
        return self._initiate_request(
            endpoint="getWebhookInfo",
            method="GET",
        )

    def set_webhook(self, webhook_url):
        """
        Register a webhook URL with Telegram.

        Args:
            webhook_url (str): Public HTTPS endpoint that receives Telegram updates.

        Sample response:
        {
            "ok": True,
            "result": True,
            "description": "Webhook was set"
        }
        """
        return self._initiate_request(
            endpoint="setWebhook",
            payload={"url": webhook_url},
            method="POST",
        )

    def send_message(self, message):
        """
        Send a text message to the configured Telegram chat.

        Args:
            message (str): Text message to send.

        Sample response:
        {
            "ok": True,
            "result": {
                "message_id": 15,
                "chat": {
                    "id": 123456789,
                    "type": "private"
                },
                "text": "Anime API encountered an error!"
            }
        }
        """
        return self._initiate_request(
            endpoint="sendMessage",
            payload={
                "chat_id": settings.TELEGRAM_CHAT_ID,
                "text": message,
            },
            method="POST",
        )
