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


class NtfyEngine:
    """ntfy HTTP pub-sub topic notification engine (ntfy.sh or self-hosted)."""

    def send(self, outbox, provider) -> dict:
        base_url = (provider.base_url or getattr(settings, 'NTFY_BASE_URL', 'https://ntfy.sh')).rstrip('/')
        topic = (outbox.outbox_for or '').lstrip('/')
        if not topic:
            return {'success': False, 'error': {'message': 'ntfy topic (outbox_for) is required'}}

        endpoint = f'{base_url}/{topic}'
        timeout = int(getattr(settings, 'TIMEOUT', 30) or 30)
        data_dict = outbox.data if isinstance(outbox.data, dict) else {}

        headers = {}
        credential = provider.credential
        if credential and credential.api_key:
            headers['Authorization'] = f'Bearer {credential.api_key}'

        if outbox.title:
            headers['Title'] = str(outbox.title)
        if outbox.url:
            headers['Click'] = str(outbox.url)
        if data_dict.get('priority') is not None:
            headers['Priority'] = str(data_dict['priority'])
        if data_dict.get('tags'):
            tags = data_dict['tags']
            headers['Tags'] = ','.join(tags) if isinstance(tags, list) else str(tags)
        if data_dict.get('markdown'):
            headers['Markdown'] = 'yes'
        if data_dict.get('actions'):
            headers['Actions'] = str(data_dict['actions'])
        if data_dict.get('attach'):
            headers['Attach'] = str(data_dict['attach'])
        if data_dict.get('filename'):
            headers['Filename'] = str(data_dict['filename'])

        logger.info(f'[NTFY SEND] POST {endpoint}')
        response = requests.post(
            endpoint,
            data=(outbox.message or '').encode('utf-8'),
            headers=headers,
            timeout=timeout,
        )
        if response.status_code not in (HTTPStatus.OK, HTTPStatus.CREATED):
            return {'success': False, 'error': _parse_error(response)}

        res = response.json()
        return {'success': True, 'id': res.get('id'), 'raw': res}
