from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from simple_history.signals import post_create_historical_record

from .site_offline_models import site_offline_models, ModelNotRegistered


@receiver(post_save, sender=Token)
def create_auth_token(sender, instance, raw, created, **kwargs):
    """Create token when a user is created (from rest_framework).
    """
    if not raw:
        if created:
            sender.objects.create(user=instance)


@receiver(m2m_changed, weak=False, dispatch_uid="serialize_m2m_on_save")
def serialize_m2m_on_save(sender, action, instance, using, **kwargs):
    """ Part of the serialize transaction process that ensures m2m are
    serialized correctly.

    Skip those not registered.
    """
    if action == "post_add":
        try:
            wrapped_instance = site_offline_models.get_wrapped_instance(instance)
        except ModelNotRegistered:
            pass
        else:
            wrapped_instance.to_outgoing_transaction(using, created=True)


@receiver(post_save, weak=False, dispatch_uid="serialize_on_save")
def serialize_on_save(sender, instance, raw, created, using, **kwargs):
    """ Serialize the model instance as an OutgoingTransaction.

    Skip those not registered.
    """
    if not raw:
        if "historical" not in instance._meta.label_lower:
            try:
                wrapped_instance = site_offline_models.get_wrapped_instance(instance)
            except ModelNotRegistered:
                pass
            else:
                wrapped_instance.to_outgoing_transaction(using, created=created)


@receiver(
    post_create_historical_record,
    weak=False,
    dispatch_uid="serialize_history_on_post_create",
)
def serialize_history_on_post_create(history_instance, using, **kwargs):
    """ Serialize the history instance as an OutgoingTransaction.

    Skip those not registered.
    """
    try:
        wrapped_instance = site_offline_models.get_wrapped_instance(history_instance)
    except ModelNotRegistered:
        pass
    else:
        wrapped_instance.to_outgoing_transaction(using, created=True)


@receiver(post_delete, weak=False, dispatch_uid="serialize_on_post_delete")
def serialize_on_post_delete(sender, instance, using, **kwargs):
    """Creates a serialized OutgoingTransaction when
    a model instance is deleted.

    Skip those not registered.
    """
    try:
        wrapped_instance = site_offline_models.get_wrapped_instance(instance)
    except ModelNotRegistered:
        pass
    else:
        wrapped_instance.to_outgoing_transaction(using, created=False, deleted=True)
