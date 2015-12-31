from django.core import serializers
from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver
from django.utils import timezone

from edc_base.encrypted_fields import FieldCryptor

from ..exceptions import SyncError

from .incoming_transaction import IncomingTransaction
from .outgoing_transaction import OutgoingTransaction
from .transaction_producer import transaction_producer


@receiver(post_save, weak=False, dispatch_uid="deserialize_to_inspector_on_post_save")
def deserialize_to_inspector_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw:
        try:
            instance.deserialize_to_inspector_on_post_save(instance, raw, created, using, **kwargs)
        except AttributeError as e:
            if 'deserialize_to_inspector_on_post_save' not in str(e):
                raise AttributeError(str(e))


@receiver(m2m_changed, weak=False, dispatch_uid='serialize_m2m_on_save')
def serialize_m2m_on_save(sender, action, instance, using, **kwargs):
    """ Part of the serialize transaction process that ensures m2m are
    serialized correctly.
    """
    if action == 'post_add':
        try:
            instance.to_outgoing_transaction(created=True)
        except AttributeError as e:
            if 'to_outgoing_transaction' not in str(e):
                raise AttributeError(str(e))


@receiver(post_save, weak=False, dispatch_uid='serialize_on_save')
def serialize_on_save(sender, instance, raw, created, using, **kwargs):
    """ Serialize the model instance as an OutgoingTransaction."""
    if not raw:
        try:
            instance.to_outgoing_transaction(created, using)
        except AttributeError as e:
            if 'to_outgoing_transaction' not in str(e):
                raise AttributeError(str(e))


@receiver(post_save, sender=IncomingTransaction, dispatch_uid="deserialize_on_post_save")
def deserialize_on_post_save(sender, instance, raw, created, using, **kwargs):
    pass
    """ Callback to deserialize an incoming transaction.

    as long as the transaction is not consumed or in error"""


@receiver(post_delete, weak=False, dispatch_uid="serialize_on_post_delete")
def serialize_on_post_delete(sender, instance, using, **kwargs):
    """Creates a serialized OutgoingTransaction when a model instance is deleted."""
    using = using or 'default'
    try:
        if instance.is_serialized() or instance._meta.proxy:
            json_obj = serializers.serialize("json", [instance, ], ensure_ascii=False, use_natural_keys=True)
            try:
                # encrypt before saving to OutgoingTransaction
                json_tx = FieldCryptor('aes', 'local').encrypt(json_obj)
            except NameError:
                pass
            except AttributeError:
                pass
            OutgoingTransaction.objects.using(using).create(
                tx_name=instance._meta.object_name,
                tx_pk=instance.pk,
                tx=json_tx,
                timestamp=timezone.now().strftime('%Y%m%d%H%M%S%f'),
                producer=transaction_producer,
                action='D')
    except AttributeError as e:
        if 'is_serialized' not in str(e):
            raise SyncError(str(e))
