import logging
from core.apis.viewsets import DevExtremeModelViewSet
from notification import settings
from notification.models import Credential
from notification.apis.serializers.credential import CredentialSerializer

logger = logging.getLogger(__name__)


class CredentialViewSet(DevExtremeModelViewSet):
    permission_classes = []
    serializer_class = CredentialSerializer
    queryset = Credential.objects.using(settings.get_db()).all()
