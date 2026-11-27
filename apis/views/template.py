import logging
from core.apis.viewsets import DevExtremeModelViewSet
from notification import settings
from notification.models import Template
from notification.apis.serializers.template import TemplateSerializer

logger = logging.getLogger(__name__)


class TemplateViewSet(DevExtremeModelViewSet):
    permission_classes = []
    serializer_class = TemplateSerializer
    queryset = Template.objects.using('NOTIFICATION').all()
