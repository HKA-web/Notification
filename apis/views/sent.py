import logging
from core.apis.viewsets import DevExtremeModelViewSet
from notification import settings
from notification.models import Sent
from notification.apis.serializers.sent import SentSerializer

logger = logging.getLogger(__name__)


class SentViewSet(DevExtremeModelViewSet):
    permission_classes = []
    serializer_class = SentSerializer
    queryset = Sent.objects.using('NOTIFICATION').all()
