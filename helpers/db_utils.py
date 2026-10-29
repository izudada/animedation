import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _


def generate_id():
    return uuid.uuid4().hex


def generate_session_id():
    return f"SESSION-{generate_id()}"


class BaseModel(models.Model):
    id = models.CharField(
        max_length=60, primary_key=True, default=generate_id, editable=False
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

