from django.contrib import admin
from edc_base.modeladmin.admin import BaseModelAdmin
from ..models import Producer
from ..actions import reset_producer_status, toggle_producer_is_active, update_producer_from_settings_file


class ProducerAdmin(BaseModelAdmin):

    list_display = ('name', 'url', 'producer_ip', 'is_active', 'sync_datetime', 'sync_status', 'comment')
    list_filter = ('is_active', 'sync_datetime', 'sync_status',)

    actions = [reset_producer_status, update_producer_from_settings_file, toggle_producer_is_active]

admin.site.register(Producer, ProducerAdmin)
