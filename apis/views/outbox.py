import logging
from core.apis.viewsets import DevExtremeModelViewSet
from notification import settings
from notification.models import Outbox
from notification.apis.serializers.outbox import OutboxSerializer

logger = logging.getLogger(__name__)


class OutboxViewSet(DevExtremeModelViewSet):
    permission_classes = []
    serializer_class = OutboxSerializer
    queryset = Outbox.objects.using('NOTIFICATION').all()
