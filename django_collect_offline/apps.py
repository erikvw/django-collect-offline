import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

from .site_offline_models import site_offline_models

style = color_style()


class OfflineConfigError(Exception):
    pass


class AppConfig(DjangoAppConfig):
    name = "django_collect_offline"
    verbose_name = "Django Collect Offline"
    base_template_name = "django_collect_offline/base.html"
    custom_json_parsers = []
    django_collect_offline_files_using = True

    # see edc_device for ROLE

    def ready(self):
        from .signals import (
            create_auth_token,  # noqa
            serialize_on_post_delete,  # noqa
            serialize_m2m_on_save,  # noqa
            serialize_on_save,  # noqa
            serialize_history_on_post_create,  # noqa
        )

        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        site_offline_models.autodiscover()
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
