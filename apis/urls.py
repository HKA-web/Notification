from django.urls import path, include
from rest_framework import routers

from notification.apis import views

router = routers.DefaultRouter()
router.register('credential', views.CredentialViewSet, basename='credential')
router.register('provider', views.ProviderViewSet, basename='provider')
router.register('template', views.TemplateViewSet, basename='template')
router.register('outbox', views.OutboxViewSet, basename='outbox')
router.register('sent', views.SentViewSet, basename='sent')

app_name = 'api'
urlpatterns = [
    path('', include(router.urls), name='api'),
]
