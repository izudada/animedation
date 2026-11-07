from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class RecommendationType(TextChoices):
    GENRE = 'GENRE', _('Genre')
    RATING = 'RATING', _('Rating')
    SYNOPSIS = 'SYNOPSIS', _('Synopsis')
    AI = 'AI', _('AI')
