import logging
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.fields import ShortUUIDField, StatusField
from core.models import Base
from notification import settings

logger = logging.getLogger(__name__)


class Provider(Base):
    """Notification channel provider configuration (onesignal or ntfy)."""

    TYPE_ONESIGNAL = 'onesignal'
    TYPE_NTFY = 'ntfy'
    TYPE_CHOICES = (
        (TYPE_ONESIGNAL, 'OneSignal'),
        (TYPE_NTFY, 'ntfy'),
    )

    provider_id = ShortUUIDField(
        length=25,
        primary_key=True,
        verbose_name=_('provider id'),
        help_text=_('Used for identity'),
    )
    provider_name = models.CharField(
        max_length=255,
        verbose_name=_('provider name'),
        help_text=_('Human readable provider/app name'),
    )
    provider_type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        default=TYPE_ONESIGNAL,
        verbose_name=_('provider type'),
        help_text=_('Notification engine type: onesignal or ntfy'),
    )
    app_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('app id'),
        help_text=_('OneSignal App ID (required for onesignal provider)'),
    )
    base_url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('base url'),
        help_text=_('Optional custom base URL (e.g. self-hosted ntfy server)'),
    )
    data = models.JSONField(
        default=dict,
        verbose_name=_('data'),
        help_text=_('Additional provider metadata'),
    )
    status = StatusField(transition=False)

    class Meta:
        managed = False
        db_table = u'"{}"."provider"'.format(settings.SCHEMA)
        verbose_name = _('Provider')
        permissions = []

    @property
    def credential(self):
        from notification.models import Credential
        return Credential.objects.using(settings.get_db()).filter(provider_id=self.provider_id, is_removed=False).first()
