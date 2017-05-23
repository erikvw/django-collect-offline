from django.contrib.admin.sites import AdminSite


class EdcSyncAdminSite(AdminSite):
    site_header = 'Edc Sync'
    site_title = 'Edc Sync'
    index_title = 'Edc Sync Administration'
    site_url = '/edc_sync/'


edc_sync_admin = EdcSyncAdminSite(name='edc_sync_admin')
