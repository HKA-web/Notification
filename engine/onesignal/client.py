import logging
from http import HTTPStatus

import requests

from notification import settings

logger = logging.getLogger(__name__)


def _parse_error(response):
    try:
        return response.json()
    except Exception:
        return {'status_code': response.status_code, 'text': response.text}


class OneSignalEngine:
    """OneSignal REST API v1 push notification engine (Mobile & Web)."""

    def _build_target(self, target_type: str, target_value: str, data_dict: dict) -> dict:
        if target_type == 'external_id':
            targets = target_value if isinstance(target_value, list) else [target_value]
            return {
                'include_aliases': {'external_id': targets},
                'target_channel': 'push',
            }
        if target_type == 'tag':
            tag_value = str(data_dict.get('tag_value', '1'))
            return {
                'filters': [{'field': 'tag', 'key': target_value, 'relation': '=', 'value': tag_value}],
            }
        if target_type == 'segment':
            segments = target_value if isinstance(target_value, list) else [target_value]
            return {'included_segments': segments}
        if target_type == 'subscription_id':
            ids = target_value if isinstance(target_value, list) else [target_value]
            return {'include_subscription_ids': ids}
        raise ValueError(f'Unsupported OneSignal target_type: {target_type!r}')

    def send(self, outbox, provider) -> dict:
        credential = provider.credential
        if not credential or not credential.api_key:
            return {'success': False, 'error': {'message': 'OneSignal REST API key not configured'}}
        if not provider.app_id:
            return {'success': False, 'error': {'message': 'OneSignal app_id not configured'}}

        base_url = (provider.base_url or getattr(settings, 'ONESIGNAL_BASE_URL', 'https://api.onesignal.com')).rstrip('/')
        endpoint = f'{base_url}/notifications?c=push'
        timeout = int(getattr(settings, 'TIMEOUT', 30) or 30)
        data_dict = outbox.data if isinstance(outbox.data, dict) else {}

        payload = {
            'app_id': provider.app_id,
            'contents': {'en': outbox.message or ''},
            **self._build_target(outbox.target_type or 'external_id', outbox.outbox_for, data_dict),
        }
        if outbox.title:
            payload['headings'] = {'en': outbox.title}
        if outbox.url:
            payload['url'] = outbox.url

        for optional_key in ('big_picture', 'small_icon', 'large_icon', 'buttons', 'web_buttons', 'priority', 'ttl'):
            if optional_key in data_dict:
                payload[optional_key] = data_dict[optional_key]
        if isinstance(data_dict.get('custom_data'), dict):
            payload['data'] = data_dict['custom_data']

        headers = {
            'Authorization': f'Key {credential.api_key}',
            'Content-Type': 'application/json; charset=utf-8',
        }

        logger.info(f'[ONESIGNAL SEND] POST {endpoint} -> {outbox.target_type}:{outbox.outbox_for}')
        response = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)
        if response.status_code not in (HTTPStatus.OK, HTTPStatus.CREATED):
            return {'success': False, 'error': _parse_error(response)}

        res = response.json()
        if res.get('errors'):
            return {'success': False, 'error': res}

        return {'success': True, 'id': res.get('id'), 'raw': res}
