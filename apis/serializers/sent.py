import logging
from core.apis.datetime import DateTimeModelSerializer
from library.restframeworkflexfields import FlexFieldsModelSerializer
from notification.apis.serializers.base import DbRoutingSerializerMixin
from notification.models import Sent

logger = logging.getLogger(__name__)


class SentSerializer(DbRoutingSerializerMixin, FlexFieldsModelSerializer, DateTimeModelSerializer):
    class Meta:
        model = Sent
        fields = [
            'base64pk',
            'sent_id',
            'template_id',
            'title',
            'message',
            'target_type',
            'sent_for',
            'url',
            'sent_date',
            'prepare_date',
            'retry',
            'scheduled',
            'scheduled_date',
            'data',
            'provider_id',
            'status',
            'created',
            'modified',
            'read_only',
            'enable',
            'properties',
            'description',
        ]
        extra_kwargs = {
            'base64pk': {'required': False},
            'sent_id': {'required': False},
        }
        expandable_fields = {
            'provider': ('notification.apis.serializers.ProviderSerializer', {'many': False}),
        }
