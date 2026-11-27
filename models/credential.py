import logging
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.fields import ShortUUIDField, StatusField
from core.models import Base

logger = logging.getLogger(__name__)


class Credential(Base):
    """Stores provider credentials (OneSignal REST API key or ntfy token) in public schema."""

    credential_id = ShortUUIDField(
        length=25,
        primary_key=True,
        verbose_name=_('credential id'),
        help_text=_('Used for identity'),
    )
    provider_id = models.CharField(
        max_length=25,
        unique=True,
        verbose_name=_('provider id'),
        help_text=_('Linked notification provider id'),
    )
    api_key = models.CharField(
        max_length=512,
        verbose_name=_('api key'),
        help_text=_('OneSignal REST API Key or ntfy Bearer token'),
    )
    status = StatusField(transition=False)

    class Meta:
        managed = False
        db_table = '"public"."notification_credential"'
        verbose_name = _('Notification Credential')
        permissions = []
