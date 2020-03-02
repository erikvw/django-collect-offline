import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

from .site_offline_models import site_offline_models
from . import get_offline_enabled

style = color_style()


class OfflineConfigError(Exception):
    pass


class AppConfig(DjangoAppConfig):
    name = "django_collect_offline"
    verbose_name = "Django Collect Offline"
    base_template_name = "django_collect_offline/base.html"
    custom_json_parsers = []
    django_collect_offline_files_using = True
    include_in_administration_section = True

    # see edc_device for ROLE

    def ready(self):
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        if get_offline_enabled():
            site_offline_models.autodiscover()
        else:
            sys.stdout.write(f"   {self.verbose_name} is disabled.\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
