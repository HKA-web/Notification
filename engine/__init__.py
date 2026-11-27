from notification.engine.onesignal import OneSignalEngine
from notification.engine.ntfy import NtfyEngine

ENGINES = {
    'onesignal': OneSignalEngine(),
    'ntfy': NtfyEngine(),
}


def get_engine(provider_type: str):
    """Return the notification engine instance for the given provider_type."""
    key = (provider_type or '').strip().lower()
    engine = ENGINES.get(key)
    if not engine:
        raise ValueError(f'Unsupported notification provider type: {provider_type!r}')
    return engine


__all__ = ['ENGINES', 'get_engine', 'OneSignalEngine', 'NtfyEngine']
