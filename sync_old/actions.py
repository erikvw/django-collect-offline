from django.contrib import messages

from edc.core.crypto_fields.classes import FieldCryptor

from .classes import SerializeToTransaction
from .exceptions import ProducerError
from .utils import update_producer_from_settings


def update_producer_from_settings_file(modeladmin, request, queryset):
    for qs in queryset:
        try:
            producer = update_producer_from_settings(qs)
            messages.add_message(request, messages.SUCCESS,
                                 'Producer {} has been updated.'.format(producer))
        except ProducerError as producer_error:
            messages.add_message(request, messages.ERROR, str(producer_error))
update_producer_from_settings_file.short_description = (
    "Update active producer from settings file (settings_key must match)")


def serialize(modeladmin, request, queryset):

    """ for a model instance serializing to outgoing"""
    serialize_to_transaction = SerializeToTransaction()
    n = 0
    for instance in queryset:
        raw = False
        created = True
        using = 'default'
        serialize_to_transaction.serialize(instance.__class__, instance, raw, created, using)
        n += 1
    messages.add_message(request, messages.SUCCESS, '%s transactions have been sent to Outgoing' % (n,))
serialize.short_description = "Send as Outgoing Transaction"


def reset_transaction_as_not_consumed(modeladmin, request, queryset):
    """ reset transaction by setting is_consumed = False"""
    for qs in queryset:
        qs.is_consumed = False
        qs.consumer = None
        qs.save()
reset_transaction_as_not_consumed.short_description = "Set transactions as NOT consumed (is_consumed=False)"


def reset_outgoing_transaction_server_as_not_consumed(modeladmin, request, queryset):
    """ reset transaction by setting is_consumed_server = False"""
    for qs in queryset:
        qs.is_consumed_server = False
        qs.consumer = None
        qs.save()
reset_outgoing_transaction_server_as_not_consumed.short_description = (
    "Set transactions as NOT consumed by Server(is_consumed_server=False)")


def reset_outgoing_transaction_server_as_consumed(modeladmin, request, queryset):
    """ reset transaction by setting is_consumed_server = True"""
    for qs in queryset:
        qs.is_consumed_server = True
        qs.consumer = None
        qs.save()
reset_outgoing_transaction_server_as_consumed.short_description = (
    "Set transactions as consumed by Server(is_consumed_server=True)")


def reset_outgoing_transaction_middle_as_not_consumed(modeladmin, request, queryset):
    """ reset transaction by setting is_consumed_middleman = False"""
    for qs in queryset:
        qs.is_consumed_middleman = False
        qs.consumer = None
        qs.save()
reset_outgoing_transaction_middle_as_not_consumed.short_description = (
    "Set transactions as NOT consumed by MiddleMan(is_consumed_middleman=False)")


def reset_outgoing_transaction_middle_as_consumed(modeladmin, request, queryset):
    """ reset transaction by setting is_consumed_middleman = True"""
    for qs in queryset:
        qs.is_consumed_middleman = True
        qs.consumer = None
        qs.save()
reset_outgoing_transaction_middle_as_consumed.short_description = (
    "Set transactions as consumed by MiddleMan(is_consumed_middleman=True)")


def reset_transaction_as_consumed(modeladmin, request, queryset):
    """ reset transaction by setting is_consumed = True"""
    for qs in queryset:
        qs.is_consumed = True
        qs.save()
reset_transaction_as_consumed.short_description = "Set transactions as consumed (is_consumed=True)"


def reset_transaction_as_ignored_and_consumed(modeladmin, request, queryset):
    """ reset transaction by setting is_ignored = True and is_consumed = True"""
    for qs in queryset:
        qs.is_consumed = True
        qs.is_ignored = True
        qs.save()
reset_transaction_as_ignored_and_consumed.short_description = (
    "Set transactions as ignored and consumed (is_ignored=True, is_consumed=True)")


def reset_producer_status(modeladmin, request, queryset):
    """ reset producer status to '-' """
    for qs in queryset:
        if qs.is_active:
            qs.sync_status = '-'
            qs.save()
reset_producer_status.short_description = "Reset producer status to '-'"


def reset_incomingtransaction_error_status(modeladmin, request, queryset):
    """ reset producer status to '-' """
    for qs in queryset:
        qs.is_error = False
        qs.error = None
        qs.save()
reset_incomingtransaction_error_status.short_description = "Reset transaction error status (is_error=False)"


def set_incomingtransaction_as_ignore_status(modeladmin, request, queryset):
    """ set incoming transaction to ignore = true """
    for qs in queryset:
        qs.is_ignored = True
        qs.error = None
        qs.save()
set_incomingtransaction_as_ignore_status.short_description = "Set transaction ignore status (is_ignored=True)"


def reset_incomingtransaction_ignore_status(modeladmin, request, queryset):
    """ set incoming transaction to ignore = false """
    for qs in queryset:
        qs.is_ignored = False
        qs.error = None
        qs.save()
reset_incomingtransaction_ignore_status.short_description = "Reset transaction ignore status (is_ignored=False)"


def decrypt_incomingtransaction(modeladmin, request, queryset):
    """ decrypt the incoming transaction """
    cryptor = FieldCryptor('aes', 'local')
    for qs in queryset:
        tx = cryptor.decrypt(qs.tx)
        qs.tx = tx
        qs.save()
decrypt_incomingtransaction.short_description = "Decrypt the incoming transaction"


def set_incomingtransaction_audits_to_ignored(modeladmin, request, queryset):
    """ set incoming audit transaction to ignore = True """
    for qs in queryset:
        if qs.tx_name.find('Audit') != -1:
            qs.is_ignored = True
            qs.error = None
            qs.save()
set_incomingtransaction_audits_to_ignored.short_description = "Set audit transactions ignore status (is_ignored=True)"


def reset_incomingtransaction_audits(modeladmin, request, queryset):
    """ set incoming audit transaction to ignore = False """
    for qs in queryset:
        if qs.tx_name.find('Audit') != -1:
            qs.is_ignored = False
            qs.error = None
            qs.save()
reset_incomingtransaction_audits.short_description = "Reset audit transactions ignore status (is_ignored=False)"


def toggle_producer_is_active(modeladmin, request, queryset):
    """ Toggle field is_active"""
    for qs in queryset:
        if qs.is_active:
            qs.is_active = False
        else:
            qs.is_active = True
        qs.save()
toggle_producer_is_active.short_description = "Toggle producer as active or not active (is_active=True/False)"
