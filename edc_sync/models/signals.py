from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver

from . import BaseSyncUuidModel, IncomingTransaction


@receiver(post_save, weak=False, dispatch_uid="deserialize_to_inspector_on_post_save")
def deserialize_to_inspector_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw:
        try:
            # method only exists on MiddleManTransaction
            instance.deserialize_to_inspector_on_post_save(instance, raw, created, using, **kwargs)
        except AttributeError as attribute_error:
            if 'deserialize_to_inspector_on_post_save' in str(attribute_error):
                pass
            else:
                raise


@receiver(m2m_changed, weak=False, dispatch_uid='serialize_m2m_on_save')
def serialize_m2m_on_save(sender, action, instance, using, **kwargs):
    """ Part of the serialize transaction process that ensures m2m are
    serialized correctly.
    """
    if action == 'post_add':
        if isinstance(instance, BaseSyncUuidModel):
            if instance.is_serialized() or instance._meta.proxy:
                # default raw to False, created to True
                # TODO: serialize is skipped if raw is True, how should raw
                # affect serialization of m2m?
                # https://docs.djangoproject.com/en/dev/ref/signals/#m2m-changed
                action = instance.action(created=True)
                instance.to_outgoing(action, using)


@receiver(post_save, weak=False, dispatch_uid='serialize_on_save')
def serialize_on_save(sender, instance, raw, created, using, **kwargs):
    """ Serialize the model instance as an OutgoingTransaction."""
    if not raw:
        if isinstance(instance, BaseSyncUuidModel):
            if instance.is_serialized() or instance._meta.proxy:
                action = instance.action(created=created)
                instance.to_outgoing(action, using)


@receiver(post_save, sender=IncomingTransaction, dispatch_uid="deserialize_on_post_save")
def deserialize_on_post_save(sender, instance, raw, created, using, **kwargs):
    pass
    """ Callback to deserialize an incoming transaction.

    as long as the transaction is not consumed or in error"""


@receiver(post_delete, weak=False, dispatch_uid="serialize_on_post_delete")
def serialize_on_post_delete(sender, instance, using, **kwargs):
    """Creates an serialized OutgoingTransaction when a model instance is deleted."""
    # if is_serialized or instance._meta.proxy:
    try:
        action = 'D'
        instance.to_outgoing(action, using)
    except AttributeError:
        pass
