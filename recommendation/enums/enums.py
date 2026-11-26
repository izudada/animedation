from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class RecommendationType(TextChoices):
    GENRE = 'GENRE', _('GENRE')
    RATING = 'RATING', _('RATING')
    SYNOPSIS = 'SYNOPSIS', _('SYNOPSIS')
    AI = 'AI', _('AI')
    SEMANTIC = 'SEMANTIC', _('SEMANTIC')
