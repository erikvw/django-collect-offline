from django.apps import apps as django_apps
from django.contrib import admin
from django.contrib.admin.sites import AdminSite

from rest_framework.authtoken.admin import TokenAdmin
from rest_framework.authtoken.models import Token

from .actions import (
    reset_transaction_as_not_consumed, reset_transaction_as_consumed,
    reset_incomingtransaction_error_status, reset_incomingtransaction_ignore_status,
    set_incomingtransaction_as_ignore_status, set_incomingtransaction_audits_to_ignored,
    reset_incomingtransaction_audits,
    reset_outgoing_transaction_server_as_consumed,
    reset_outgoing_transaction_server_as_not_consumed, )

from .constants import SERVER, CLIENT
from .models import IncomingTransaction, OutgoingTransaction, Client, Server

edc_sync_app_config = django_apps.get_app_config('edc_sync')


class EdcSyncAdminSite(AdminSite):
    site_header = edc_sync_app_config.verbose_name
    site_title = edc_sync_app_config.verbose_name
    index_title = edc_sync_app_config.verbose_name + ' ' + 'Admin'
    site_url = '/edc-sync/'

edc_sync_admin = EdcSyncAdminSite(name='edc_sync_admin')

admin.site.unregister(Token)


@admin.register(Token, site=edc_sync_admin)
class MyTokenAdmin(TokenAdmin):
    raw_id_fields = ('user',)
    list_display = ('key', 'user', 'created')
    fields = ('user', )
    ordering = ('-created',)


@admin.register(IncomingTransaction, site=edc_sync_admin)
class IncomingTransactionAdmin (admin.ModelAdmin):

    ordering = ('-timestamp', )

    list_display = (
        'tx_name', 'view', 'producer', 'is_consumed', 'is_error',
        'is_ignored', 'consumer', 'consumed_datetime', 'action',
        'tx_pk', 'timestamp', 'hostname_modified')

    list_filter = (
        'is_consumed', 'is_error', 'is_ignored', 'consumer',
        'consumed_datetime', 'producer', 'action', 'tx_name',
        'hostname_modified')

    search_fields = ('tx_pk', 'tx', 'timestamp', 'error', 'id')

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
        'tx_name', 'view', 'producer', 'is_consumed_middleman',
        'is_consumed_server', 'is_error', 'consumer',
        'consumed_datetime', 'action', 'tx_pk', 'timestamp',
        'hostname_modified')

    list_filter = (
        'is_error', 'is_consumed_middleman', 'is_consumed_server',
        'consumer', 'consumed_datetime', 'producer',
        'action', 'tx_name', 'hostname_modified')

    search_fields = ('tx_pk', 'tx', 'timestamp', 'error', 'id')

    actions = [
        reset_outgoing_transaction_server_as_consumed,
        reset_outgoing_transaction_server_as_not_consumed]


class HostAdmin(admin.ModelAdmin):

        list_display = (
            'hostname', 'port', 'is_active',
            'last_sync_datetime', 'last_sync_status', 'comment')

        list_filter = ('is_active', 'last_sync_datetime', 'last_sync_status',)


if edc_sync_app_config.role == SERVER:
    @admin.register(Client, site=edc_sync_admin)
    class ClientAdmin(HostAdmin):
        pass

if edc_sync_app_config.role == CLIENT:
    @admin.register(Server, site=edc_sync_admin)
    class ServerAdmin(HostAdmin):
        pass
