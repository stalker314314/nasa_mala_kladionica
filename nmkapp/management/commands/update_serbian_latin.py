# -*- coding: utf-8 -*-

import os
from transliterate import translit

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Updates Serbian latin translation'

    def handle(self, *args, **options):
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
        locale_dir = os.path.join(root_dir, 'locale')
        with open(os.path.join(locale_dir, 'sr', 'LC_MESSAGES', 'django.po'), 'rb') as sr_file:
            sr_content = sr_file.read().decode('utf-8')
        sr_latn_content = translit(sr_content, language_code='sr', reversed=True)
        with open(os.path.join(
                locale_dir, 'sr_Latn', 'LC_MESSAGES', 'django.po'), 'w', encoding='utf-8') as sr_latn_file:
            sr_latn_file.write(sr_latn_content)
        self.stdout.write(self.style.SUCCESS('Done'))
