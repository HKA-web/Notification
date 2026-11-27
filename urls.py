import logging
from django.urls import path, include

logger = logging.getLogger(__name__)

app_name = 'notification'
urlpatterns = [
    path('api/', include('notification.apis.urls'), name='api'),
]
