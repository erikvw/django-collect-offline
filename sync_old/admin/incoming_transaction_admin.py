from django.contrib import admin
from edc.base.modeladmin.admin import BaseModelAdmin
from ..models import IncomingTransaction
from ..actions import reset_transaction_as_not_consumed, reset_transaction_as_consumed, reset_incomingtransaction_error_status, reset_incomingtransaction_ignore_status, \
                    set_incomingtransaction_as_ignore_status, set_incomingtransaction_audits_to_ignored, reset_incomingtransaction_audits


class IncomingTransactionAdmin (BaseModelAdmin):

    list_display = ('tx_name', 'render', 'producer', 'is_consumed', 'is_error', 'is_ignored', 'consumer', 'consumed_datetime', 'action', 'tx_pk', 'timestamp', 'hostname_modified')

    list_filter = ('is_consumed', 'is_error', 'is_ignored', 'consumer', 'consumed_datetime', 'producer', 'action', 'tx_name', 'hostname_modified')

    search_fields = ('tx_pk', 'tx', 'timestamp', 'error')

    actions = [reset_transaction_as_not_consumed, reset_transaction_as_consumed, reset_incomingtransaction_error_status, set_incomingtransaction_as_ignore_status, \
               reset_incomingtransaction_ignore_status,  set_incomingtransaction_audits_to_ignored, reset_incomingtransaction_audits]

admin.site.register(IncomingTransaction, IncomingTransactionAdmin)
