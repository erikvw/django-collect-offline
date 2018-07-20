import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

from .site_offline_models import site_offline_models

style = color_style()


class OfflineConfigError(Exception):
    pass


class AppConfig(DjangoAppConfig):
    name = 'django_collect_offline'
    verbose_name = 'Offline Synchronization'
    base_template_name = 'edc_base/base.html'
    custom_json_parsers = []
    django_collect_offline_files_using = True

    # see edc_device for ROLE

    def ready(self):
        from .signals import (
            create_auth_token, serialize_on_post_delete,
            serialize_m2m_on_save, serialize_on_save)
        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        site_offline_models.autodiscover()
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')
