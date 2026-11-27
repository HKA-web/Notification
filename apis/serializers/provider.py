import logging
from core.apis.datetime import DateTimeModelSerializer
from library.restframeworkflexfields import FlexFieldsModelSerializer
from notification.apis.serializers.base import DbRoutingSerializerMixin
from notification.models import Provider

logger = logging.getLogger(__name__)


class ProviderSerializer(DbRoutingSerializerMixin, FlexFieldsModelSerializer, DateTimeModelSerializer):
    class Meta:
        model = Provider
        fields = [
            'base64pk',
            'provider_id',
            'provider_name',
            'provider_type',
            'app_id',
            'base_url',
            'data',
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
            'provider_id': {'required': False},
            'provider_type': {'required': False},
            'app_id': {'required': False, 'allow_null': True, 'allow_blank': True},
            'base_url': {'required': False, 'allow_null': True, 'allow_blank': True},
            'data': {'required': False},
            'status': {'required': False},
            'created': {'required': False},
            'modified': {'required': False},
            'read_only': {'required': False},
            'enable': {'required': False},
            'properties': {'required': False},
            'description': {'required': False},
        }
