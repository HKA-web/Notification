import logging
from core.apis.viewsets import DevExtremeModelViewSet
from notification import settings
from notification.models import Provider
from notification.apis.serializers.provider import ProviderSerializer

logger = logging.getLogger(__name__)


class ProviderViewSet(DevExtremeModelViewSet):
    permission_classes = []
    serializer_class = ProviderSerializer
    queryset = Provider.objects.using('NOTIFICATION').all()
