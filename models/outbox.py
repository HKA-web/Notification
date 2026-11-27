import logging
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.fields import ShortUUIDField, StatusField
from core.models import Base
from core.utils import ShortUUID
from notification import settings

logger = logging.getLogger(__name__)


class Outbox(Base):
    """Outbound notification queue item dispatched via OneSignal or ntfy engine."""

    TARGET_EXTERNAL_ID = 'external_id'
    TARGET_TAG = 'tag'
    TARGET_SEGMENT = 'segment'
    TARGET_SUBSCRIPTION_ID = 'subscription_id'
    TARGET_TOPIC = 'topic'

    outbox_id = ShortUUIDField(
        length=25,
        max_length=100,
        primary_key=True,
        verbose_name=_('outbox id'),
        help_text=_('Used for identity'),
    )
    sent_id = ShortUUIDField(
        length=25,
        max_length=100,
        verbose_name=_('sent id'),
        help_text=_('Used for identity when notification is sent'),
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
        default=TARGET_EXTERNAL_ID,
        verbose_name=_('target type'),
        help_text=_('Target type: external_id, tag, segment, subscription_id, or topic'),
    )
    outbox_for = models.CharField(
        max_length=255,
        verbose_name=_('outbox for'),
        help_text=_('Target external_id (e.g. app_userid), topic, tag, segment, or subscription_id'),
    )
    url = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('url'),
        help_text=_('Optional click/action URL'),
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
        help_text=_('Extra provider payload options (priority, tags, icon, buttons, etc.)'),
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
        db_table = u'"{}"."outbox"'.format(settings.SCHEMA)
        verbose_name = _('Outbox')
        permissions = []

    @property
    def provider(self):
        if self.provider_id:
            from notification.models import Provider
            return Provider.objects.using(settings.get_db()).filter(pk=self.provider_id).first()
        return None

    @property
    def template(self):
        if getattr(self, 'template_id', None):
            from notification.models import Template
            return Template.objects.using(settings.get_db()).filter(pk=self.template_id).first()
        return None

    def render(self):
        """Render message and optional title from linked Django Template."""
        if not self.template:
            return
        if self.template.provider_id and self.template.provider_id != self.provider_id:
            from notification.models import Template
            raise Template.DoesNotExist('Template matching query does not exist')

        from django.template import Template as DjangoTemplate, Context
        ctx = Context(dict(self.data or {}, **(self.properties or {})))
        if not self.message:
            setattr(self, 'message', DjangoTemplate(self.template.template).render(ctx))
        if not self.title and self.template.title_template:
            setattr(self, 'title', DjangoTemplate(self.template.title_template).render(ctx))

    def _record_failure(self, db, error_detail):
        data_dict = dict(self.data) if isinstance(self.data, dict) else {}
        data_dict['error'] = error_detail
        self.data = data_dict
        self.save(using=db, update_fields=['data'])
        try:
            from notification import signals as notif_signals
            notif_signals.notification_failed.send(
                sender=self.__class__,
                instance=self,
                error=error_detail,
            )
        except Exception as sig_err:
            logger.error(f"Error triggering notification_failed signal: {sig_err}")

    def send(self):
        """Dispatch this outbox item via the configured provider engine."""
        from notification.engine import get_engine
        from notification.models import Sent

        db = settings.get_db()
        self.refresh_from_db(using=db)

        provider = self.provider
        if not provider:
            err = {'message': f'Provider {self.provider_id} not found'}
            logger.error(f"[NOTIFICATION OUTBOX FAILED] {err}")
            self._record_failure(db, err)
            return self

        try:
            engine = get_engine(provider.provider_type)
            result = engine.send(self, provider)
        except Exception as exc:
            logger.error(f"[NOTIFICATION OUTBOX EXCEPTION] {self.pk}: {exc}", exc_info=True)
            self._record_failure(db, str(exc))
            return self

        if not result.get('success'):
            err = result.get('error') or {'message': 'Unknown provider error'}
            logger.error(f"[NOTIFICATION OUTBOX FAILED] {provider.provider_type}: {err}")
            self._record_failure(db, err)
            return self

        msg_id = result.get('id') or self.sent_id or ShortUUID().random(length=25)
        props_dict = dict(self.properties) if isinstance(self.properties, dict) else {}
        value = dict(
            template_id=self.template_id,
            title=self.title,
            message=self.message,
            target_type=self.target_type,
            sent_for=self.outbox_for,
            url=self.url,
            sent_date=timezone.now(),
            prepare_date=self.prepare_date or timezone.now(),
            retry=self.retry,
            scheduled=self.scheduled,
            scheduled_date=self.scheduled_date,
            provider_id=self.provider_id,
            data=result.get('raw', {}),
            properties=dict(props_dict, outbox=self.pk),
        )
        sent, _ = Sent.objects.using(db).get_or_create(pk=msg_id, defaults=value)

        try:
            from notification import signals as notif_signals
            notif_signals.notification_sent.send(
                sender=self.__class__,
                instance=sent,
                outbox=self,
                result=result,
            )
        except Exception as sig_err:
            logger.error(f"Error triggering notification_sent signal: {sig_err}")

        self.delete(using=db, soft=False)
        return self


@receiver(signals.pre_save, sender=Outbox)
def on_outbox_create(sender, instance: Outbox, **kwargs):
    if instance and instance._state.adding:
        instance.render()


@receiver(signals.post_save, sender=Outbox)
def on_outbox_created(sender, instance: Outbox, created, **kwargs):
    if instance and created and not instance.scheduled:
        try:
            from notification.tasks import process_outbox
            process_outbox(instance)
        except Exception as e:
            logger.warning(f"Huey enqueue error ({e}), processing outbox directly.")
            instance.send()
