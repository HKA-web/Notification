import logging
from core.apis.datetime import DateTimeModelSerializer
from library.restframeworkflexfields import FlexFieldsModelSerializer
from notification.apis.serializers.base import DbRoutingSerializerMixin
from notification.models import Template

logger = logging.getLogger(__name__)


class TemplateSerializer(DbRoutingSerializerMixin, FlexFieldsModelSerializer, DateTimeModelSerializer):
    class Meta:
        model = Template
        fields = [
            'base64pk',
            'template_id',
            'template_name',
            'title_template',
            'template',
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
            'template_id': {'required': False},
            'title_template': {'required': False, 'allow_null': True, 'allow_blank': True},
            'provider_id': {'required': False, 'allow_null': True, 'allow_blank': True},
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
        }
