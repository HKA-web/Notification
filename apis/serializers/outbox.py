import logging
from core.apis.datetime import DateTimeModelSerializer
from library.restframeworkflexfields import FlexFieldsModelSerializer
from notification.apis.serializers.base import DbRoutingSerializerMixin
from notification.models import Outbox

logger = logging.getLogger(__name__)


class OutboxSerializer(DbRoutingSerializerMixin, FlexFieldsModelSerializer, DateTimeModelSerializer):
    class Meta:
        model = Outbox
        fields = [
            'base64pk',
            'outbox_id',
            'template_id',
            'title',
            'message',
            'target_type',
            'outbox_for',
            'url',
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
            'outbox_id': {'required': False},
            'template_id': {'required': False, 'allow_null': True, 'allow_blank': True},
            'title': {'required': False, 'allow_null': True, 'allow_blank': True},
            'message': {'required': False, 'allow_null': True, 'allow_blank': True},
            'target_type': {'required': False},
            'url': {'required': False, 'allow_null': True, 'allow_blank': True},
            'prepare_date': {'required': False},
            'retry': {'required': False},
            'scheduled': {'required': False},
            'scheduled_date': {'required': False},
            'data': {'required': False},
            'status': {'required': False},
            'created': {'required': False},
            'modified': {'required': False},
            'read_only': {'required': False},
            'enable': {'required': False},
            'properties': {'required': False},
            'description': {'required': False},
        }
        expandable_fields = {
            'provider': ('notification.apis.serializers.ProviderSerializer', {'many': False}),
            'template': ('notification.apis.serializers.TemplateSerializer', {'many': False}),
        }
