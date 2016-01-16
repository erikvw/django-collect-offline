from django.contrib import admin

from ..actions import (
    reset_outgoing_transaction_server_as_consumed,
    reset_outgoing_transaction_server_as_not_consumed)
from ..models import OutgoingTransaction


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

admin.site.register(OutgoingTransaction, OutgoingTransactionAdmin)
