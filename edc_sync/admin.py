from django.contrib import admin
from django.contrib.admin.sites import AdminSite

from .actions import (
    reset_transaction_as_not_consumed, reset_transaction_as_consumed,
    reset_incomingtransaction_error_status, reset_incomingtransaction_ignore_status,
    set_incomingtransaction_as_ignore_status, set_incomingtransaction_audits_to_ignored,
    reset_incomingtransaction_audits,
    reset_outgoing_transaction_server_as_consumed,
    reset_outgoing_transaction_server_as_not_consumed,
    reset_producer_status, toggle_producer_is_active, update_producer_from_settings_file)
from .models import IncomingTransaction, OutgoingTransaction, Producer, RequestLog


class EdcSyncAdminSite(AdminSite):
    site_header = 'Data Synchronization'
    site_title = 'Data Synchronization'
    index_title = 'Data Synchronization Admin'
    site_url = '/edc_sync/'

edc_sync_admin = EdcSyncAdminSite(name='edc_sync_admin')


@admin.register(IncomingTransaction, site=edc_sync_admin)
class IncomingTransactionAdmin (admin.ModelAdmin):

    ordering = ('-timestamp', )

    list_display = (
        'tx_name', 'render', 'producer', 'is_consumed', 'is_error',
        'is_ignored', 'consumer', 'consumed_datetime', 'action',
        'tx_pk', 'timestamp', 'hostname_modified')

    list_filter = (
        'is_consumed', 'is_error', 'is_ignored', 'consumer',
        'consumed_datetime', 'producer', 'action', 'tx_name',
        'hostname_modified')

    search_fields = ('tx_pk', 'tx', 'timestamp', 'error')

    actions = [
        reset_transaction_as_not_consumed,
        reset_transaction_as_consumed,
        reset_incomingtransaction_error_status,
        set_incomingtransaction_as_ignore_status,
        reset_incomingtransaction_ignore_status,
        set_incomingtransaction_audits_to_ignored,
        reset_incomingtransaction_audits]


@admin.register(OutgoingTransaction, site=edc_sync_admin)
class OutgoingTransactionAdmin (admin.ModelAdmin):

    ordering = ('-timestamp', )

    list_display = (
        'tx_name', 'render', 'producer', 'is_consumed_middleman',
        'is_consumed_server', 'is_error', 'consumer',
        'consumed_datetime', 'action', 'tx_pk', 'timestamp',
        'hostname_modified')

    list_filter = (
        'is_error', 'is_consumed_middleman', 'is_consumed_server',
        'consumer', 'consumed_datetime', 'producer',
        'action', 'tx_name', 'hostname_modified')

    search_fields = ('tx_pk', 'tx', 'timestamp', 'error')

    actions = [
        reset_outgoing_transaction_server_as_consumed,
        reset_outgoing_transaction_server_as_not_consumed]


@admin.register(Producer, site=edc_sync_admin)
class ProducerAdmin(admin.ModelAdmin):

    list_display = (
        'name', 'url', 'db_host', 'is_active',
        'sync_datetime', 'sync_status', 'comment')

    list_filter = ('is_active', 'sync_datetime', 'sync_status',)

    actions = [
        reset_producer_status,
        update_producer_from_settings_file,
        toggle_producer_is_active]


@admin.register(RequestLog, site=edc_sync_admin)
class RequestLogAdmin(admin.ModelAdmin):

    list_display = ('producer', 'request_datetime', 'status', 'comment')
