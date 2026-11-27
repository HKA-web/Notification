import logging

from django.db.models import Q
from django.utils import timezone
from huey import crontab as cron

import library.djangohuey as huey
from notification import settings
from notification.apps import ApplicationConfig
from notification.models import Outbox

logger = logging.getLogger(__name__)


@huey.db_task(name='Notification Process Outbox Task', queue=ApplicationConfig.name)
def process(outbox: Outbox):
    if outbox and not outbox.scheduled:
        db = settings.get_db()
        if outbox.prepare_date is None:
            setattr(outbox, 'prepare_date', timezone.now())
        setattr(outbox, 'retry', outbox.retry + 1)
        outbox.save(using=db, update_fields=['prepare_date', 'retry'])
        outbox.send()


@huey.db_periodic_task(cron(minute='*'), name='Notification Process Scheduled Outbox Task', queue=ApplicationConfig.name)
def process_scheduled():
    outbox_cfg = getattr(settings, 'OUTBOX', {}) if isinstance(getattr(settings, 'OUTBOX', {}), dict) else {}
    retry_maximum = int(outbox_cfg.get('RETRY', 3))
    retry_delay_minutes = int(outbox_cfg.get('DELAY', 5))
    retry_blast = bool(outbox_cfg.get('RETRY_BLAST', True))
    batch_size = int(outbox_cfg.get('BATCH_SIZE', 50))

    now = timezone.now()
    cool_down_time = now - timezone.timedelta(minutes=retry_delay_minutes)

    eligible_q = (
        (Q(retry=0) & (Q(scheduled=False) | Q(scheduled=True, scheduled_date__lte=now)))
        | (Q(retry__gt=0, retry__lte=retry_maximum, prepare_date__lte=cool_down_time))
    )

    db = settings.get_db()
    queryset = Outbox.objects.using(db).filter(eligible_q)
    if retry_blast:
        queryset = queryset.filter(~Q(properties__has_key='blast'))

    outbox_batch = list(queryset.order_by('retry', 'created')[:batch_size])
    for outbox in outbox_batch:
        outbox.prepare_date = now
        outbox.retry = outbox.retry + 1
        outbox.save(using=db, update_fields=['prepare_date', 'retry'])
        outbox.send()
