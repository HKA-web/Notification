import logging
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.fields import ShortUUIDField, StatusField
from core.models import Base
from notification import settings

logger = logging.getLogger(__name__)


class Sent(Base):
    """Sent notification history record."""

    sent_id = ShortUUIDField(
        length=25,
        max_length=100,
        primary_key=True,
        verbose_name=_('sent id'),
        help_text=_('Used for identity'),
    )
    template_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('template'),
        help_text=_('Used for linked key'),
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('title'),
        help_text=_('Notification title'),
    )
    message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('message'),
        help_text=_('Used for content'),
    )
    target_type = models.CharField(
        max_length=50,
        default='external_id',
        verbose_name=_('target type'),
        help_text=_('Target type: external_id, tag, segment, subscription_id, or topic'),
    )
    sent_for = models.CharField(
        max_length=255,
        verbose_name=_('sent for'),
        help_text=_('Target external_id, topic, tag, segment, or subscription_id'),
    )
    url = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('url'),
        help_text=_('Optional click/action URL'),
    )
    sent_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('sent date'),
        help_text=_('Used for tracking sent date'),
    )
    prepare_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('prepare date'),
        help_text=_('Used for tracking begin outbox prepared'),
    )
    retry = models.IntegerField(
        default=0,
        verbose_name=_('retry'),
        help_text=_('Used for retry send outbox'),
    )
    scheduled = models.BooleanField(
        default=False,
        verbose_name=_('scheduled'),
        help_text=_('Used for scheduled message'),
    )
    scheduled_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('scheduled date'),
        help_text=_('Used for scheduled message send date'),
    )
    data = models.JSONField(
        default=dict,
        verbose_name=_('data'),
        help_text=_('Used for data value'),
    )
    provider_id = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        verbose_name=_('provider'),
        help_text=_('Used for linked key'),
    )
    status = StatusField(transition=False)

    class Meta:
        managed = False
        db_table = u'"{}"."sent"'.format(settings.SCHEMA)
        verbose_name = _('Sent')
        permissions = []

    @property
    def provider(self):
        if self.provider_id:
            from notification.models import Provider
            return Provider.objects.using(settings.get_db()).filter(pk=self.provider_id).first()
        return None
