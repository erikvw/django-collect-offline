from django.contrib.admin.sites import AdminSite


class DjangoOfflineAdminSite(AdminSite):
    site_header = 'Django Offline'
    site_title = 'Django Offline'
    index_title = 'Django Offline Administration'
    site_url = '/administration/'


django_offline_admin = DjangoOfflineAdminSite(name='django_offline_admin')
