import logging
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from core.apis.datetime import DateTimeModelSerializer
from library.restframeworkflexfields import FlexFieldsModelSerializer
from notification import settings
from notification.apis.serializers.base import DbRoutingSerializerMixin
from notification.models import Credential

logger = logging.getLogger(__name__)


class CredentialSerializer(DbRoutingSerializerMixin, FlexFieldsModelSerializer, DateTimeModelSerializer):
    provider_id = serializers.CharField(
        max_length=25,
        validators=[UniqueValidator(queryset=Credential.objects.using(settings.get_db()).all())],
    )

    class Meta:
        model = Credential
        fields = [
            'base64pk',
            'credential_id',
            'provider_id',
            'api_key',
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
            'credential_id': {'required': False},
            'api_key': {'write_only': True},
            'status': {'required': False},
            'created': {'required': False},
            'modified': {'required': False},
            'read_only': {'required': False},
            'enable': {'required': False},
            'properties': {'required': False},
            'description': {'required': False},
        }
