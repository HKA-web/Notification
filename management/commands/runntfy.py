import os
import shutil
import subprocess
from pathlib import Path

from django.core.management.base import BaseCommand
from notification import settings

MODULE_DIR = Path(__file__).resolve().parent.parent.parent


class Command(BaseCommand):
    help = 'Management command to run portable self-hosted ntfy server'

    def add_arguments(self, parser):
        parser.add_argument(
            '--port',
            type=int,
            default=None,
            help='Port HTTP untuk server ntfy (default dari NOTIFICATION.NTFY_PORT)',
        )
        parser.add_argument(
            '--config',
            type=str,
            default=None,
            help='Path ke file server.yml ntfy',
        )

    def _resolve_ntfy_binary(self) -> str | None:
        base_dir = Path(settings.djangosettings.BASE_DIR).resolve()
        binary_name = 'ntfy.exe' if os.name == 'nt' else 'ntfy'
        local_bin = base_dir / 'bin' / 'ntfy' / binary_name
        if local_bin.exists():
            return str(local_bin)
        return shutil.which(binary_name)

    def handle(self, *args, **kwargs):
        port = kwargs.get('port') or getattr(settings, 'NTFY_PORT', 8085) or 8085
        config_path = Path(
            kwargs.get('config') or (MODULE_DIR / 'engine' / 'ntfy' / 'server.yml')
        ).resolve()

        data_dir = MODULE_DIR / 'engine' / 'ntfy' / 'data'
        (data_dir / 'attachments').mkdir(parents=True, exist_ok=True)

        ntfy_bin = self._resolve_ntfy_binary()
        if not ntfy_bin:
            binary_name = 'ntfy.exe' if os.name == 'nt' else 'ntfy'
            expected = Path(settings.djangosettings.BASE_DIR).resolve() / 'bin' / 'ntfy' / binary_name
            self.stderr.write(self.style.ERROR(
                f'Binary {binary_name} tidak ditemukan.\n'
                f'Silakan unduh release resmi dari https://github.com/binwiederhier/ntfy/releases\n'
                f'dan letakkan di: {expected}'
            ))
            return

        cmd = [
            ntfy_bin,
            'serve',
            '--config',
            str(config_path),
            '--listen-http',
            f':{port}',
        ]
        fcm_keys = list((MODULE_DIR / 'engine' / 'ntfy').glob('*.json'))
        if fcm_keys:
            self.stdout.write(self.style.SUCCESS(f'FCM wakeup aktif ({fcm_keys[0].name})'))
        self.stdout.write(self.style.SUCCESS(f'Starting self-hosted ntfy on http://127.0.0.1:{port}'))
        self.stdout.write(f'Command: {" ".join(cmd)}')
        subprocess.run(cmd, check=False)
