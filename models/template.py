import logging
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.fields import ShortUUIDField, StatusField
from core.models import Base
from notification import settings

logger = logging.getLogger(__name__)


class Template(Base):
    """Django template for notification title and message body."""

    template_id = ShortUUIDField(
        length=25,
        max_length=100,
        primary_key=True,
        verbose_name=_('template id'),
        help_text=_('Used for identity'),
    )
    template_name = models.CharField(
        max_length=255,
        verbose_name=_('template name'),
        help_text=_('Used for view'),
    )
    title_template = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('title template'),
        help_text=_('Optional Django template for notification title'),
    )
    template = models.TextField(
        verbose_name=_('template'),
        help_text=_('Django template text for notification message'),
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
        db_table = u'"{}"."template"'.format(settings.SCHEMA)
        verbose_name = _('Template')
        permissions = []

    @property
    def provider(self):
        if self.provider_id:
            from notification.models import Provider
            return Provider.objects.using(settings.get_db()).filter(pk=self.provider_id).first()
        return None
