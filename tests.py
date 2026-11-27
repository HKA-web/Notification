from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from notification.engine import get_engine
from notification.engine.ntfy import NtfyEngine
from notification.engine.onesignal import OneSignalEngine
from notification.models import Outbox


class NotificationEngineTest(SimpleTestCase):
    def test_get_engine_returns_separated_providers(self):
        self.assertIsInstance(get_engine('onesignal'), OneSignalEngine)
        self.assertIsInstance(get_engine('ntfy'), NtfyEngine)
        with self.assertRaises(ValueError):
            get_engine('unknown')

    @patch('notification.engine.onesignal.client.requests.post')
    def test_onesignal_send_external_id(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {'id': 'os-msg-1'},
        )
        provider = SimpleNamespace(
            provider_type='onesignal',
            app_id='app-uuid-1',
            base_url=None,
            credential=SimpleNamespace(api_key='os-rest-key'),
        )
        outbox = Outbox(
            target_type='external_id',
            outbox_for='myapp_123',
            title='Hello',
            message='World',
            url='https://example.com',
        )

        result = OneSignalEngine().send(outbox, provider)

        self.assertTrue(result['success'])
        self.assertEqual(result['id'], 'os-msg-1')
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs['headers']['Authorization'], 'Key os-rest-key')
        self.assertEqual(kwargs['json']['app_id'], 'app-uuid-1')
        self.assertEqual(kwargs['json']['include_aliases'], {'external_id': ['myapp_123']})
        self.assertEqual(kwargs['json']['target_channel'], 'push')
        self.assertEqual(kwargs['json']['headings'], {'en': 'Hello'})
        self.assertEqual(kwargs['json']['contents'], {'en': 'World'})
        self.assertEqual(kwargs['json']['url'], 'https://example.com')

    def test_onesignal_build_targets(self):
        engine = OneSignalEngine()
        self.assertEqual(
            engine._build_target('tag', 'promo', {}),
            {'filters': [{'field': 'tag', 'key': 'promo', 'relation': '=', 'value': '1'}]},
        )
        self.assertEqual(
            engine._build_target('segment', 'Active Users', {}),
            {'included_segments': ['Active Users']},
        )
        self.assertEqual(
            engine._build_target('subscription_id', 'sub-1', {}),
            {'include_subscription_ids': ['sub-1']},
        )

    @patch('notification.engine.ntfy.client.requests.post')
    def test_ntfy_send_topic(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {'id': 'ntfy-1', 'topic': 'server-alerts'},
        )
        provider = SimpleNamespace(
            provider_type='ntfy',
            base_url='https://ntfy.example.com',
            credential=SimpleNamespace(api_key='tk_secret'),
        )
        outbox = Outbox(
            target_type='topic',
            outbox_for='server-alerts',
            title='Alert',
            message='Disk full',
            url='https://status.example.com',
            data={'priority': 'high', 'tags': ['warning', 'floppy_disk']},
        )

        result = NtfyEngine().send(outbox, provider)

        self.assertTrue(result['success'])
        self.assertEqual(result['id'], 'ntfy-1')
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], 'https://ntfy.example.com/server-alerts')
        self.assertEqual(kwargs['data'], b'Disk full')
        self.assertEqual(kwargs['headers']['Authorization'], 'Bearer tk_secret')
        self.assertEqual(kwargs['headers']['Title'], 'Alert')
        self.assertEqual(kwargs['headers']['Priority'], 'high')
        self.assertEqual(kwargs['headers']['Tags'], 'warning,floppy_disk')
        self.assertEqual(kwargs['headers']['Click'], 'https://status.example.com')

    @patch('notification.engine.ntfy.client.requests.post')
    def test_ntfy_handles_http_error(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=403,
            text='forbidden',
            json=MagicMock(side_effect=ValueError('no json')),
        )
        provider = SimpleNamespace(provider_type='ntfy', base_url=None, credential=None)
        outbox = Outbox(target_type='topic', outbox_for='private-topic', message='hi')

        result = NtfyEngine().send(outbox, provider)

        self.assertFalse(result['success'])
        self.assertEqual(result['error']['status_code'], 403)
