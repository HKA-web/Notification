import logging
from django import dispatch

logger = logging.getLogger(__name__)

notification_sent = dispatch.Signal()
notification_failed = dispatch.Signal()
