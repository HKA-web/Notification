import logging
import sys

from django.conf import settings as djangosettings
from notification.apps import ApplicationConfig

logger = logging.getLogger(__name__)

DEFAULTS = dict(
    SECRET_KEY=str(getattr(djangosettings, 'SECRET_KEY', '')),
    SCHEMA=ApplicationConfig.name,
    ONESIGNAL_BASE_URL=getattr(djangosettings, 'NOTIFICATION.ONESIGNAL_BASE_URL', 'https://api.onesignal.com'),
    NTFY_BASE_URL=getattr(djangosettings, 'NOTIFICATION.NTFY_BASE_URL', 'https://ntfy.sh'),
    NTFY_PORT=getattr(djangosettings, 'NOTIFICATION.NTFY_PORT', 8085),
    TIMEOUT=getattr(djangosettings, 'NOTIFICATION.TIMEOUT', 30),
    OUTBOX=dict(
        RETRY=3,
        DELAY=5,
        RETRY_BLAST=True,
        BATCH_SIZE=50,
    ),
)
__all__ = list(DEFAULTS) + ['get_db']


def get_db():
    """Return 'NOTIFICATION' database alias if configured, otherwise 'default'."""
    return 'NOTIFICATION' if 'NOTIFICATION' in getattr(djangosettings, 'DATABASES', {}) else 'default'


def load():
    module = sys.modules[__name__]
    for name, default in DEFAULTS.items():
        setattr(module, name, getattr(djangosettings, ApplicationConfig.name.upper(), {}).get(name, default))


load()
