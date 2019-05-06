from django.apps import apps as django_apps
from django.contrib.admin.sites import AdminSite

app_config = django_apps.get_app_config("django_collect_offline")


class DjangoOfflineAdminSite(AdminSite):
    site_header = app_config.verbose_name
    site_title = app_config.verbose_name
    index_title = f"{app_config.verbose_name} Admin"
    site_url = "/administration/"


django_collect_offline_admin = DjangoOfflineAdminSite(
    name="django_collect_offline_admin"
)
