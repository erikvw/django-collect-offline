from django.contrib.auth.models import User as AuthUser
from edc_sync.mixins.sync_mixin import SyncMixin


class User(SyncMixin, AuthUser):

    class Meta:
        app_label = 'edc_sync'
