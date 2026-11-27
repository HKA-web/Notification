from notification.apis.views.credential import CredentialViewSet
from notification.apis.views.provider import ProviderViewSet
from notification.apis.views.template import TemplateViewSet
from notification.apis.views.outbox import OutboxViewSet
from notification.apis.views.sent import SentViewSet

__all__ = [
    'CredentialViewSet',
    'ProviderViewSet',
    'TemplateViewSet',
    'OutboxViewSet',
    'SentViewSet',
]
