from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model

from edc_base.model.models import BaseUuidModel

from ..classes import SerializeToTransaction


class BaseSyncUuidModel(BaseUuidModel):

    """Base model for all UUID models and adds synchronization
    methods and signals. """

    def serialize(self, sender, instance, raw, created, using, **kwargs):
        """Returns a serializer function."""
        return SerializeToTransaction().serialize(sender, instance, raw, created, using, **kwargs)

    def is_serialized(self, serialize=True):
        """Returns True only if ALLOW_MODEL_SERIALIZATION is explicitly
        set to True in settings.

        ALLOW_MODEL_SERIALIZATION is a required settings attribute for this module.
        """
        try:
            return settings.ALLOW_MODEL_SERIALIZATION
        except AttributeError:
            raise ImproperlyConfigured(
                'Model uses base classes from edc.sync. Add attribute '
                '\'ALLOW_MODEL_SERIALIZATION = True\' to settings to enable '
                'serialization of transactions (or = False to disable).')

    def skip_saving_criteria(self):
        """Users may override to avoid saving/persisting instances of a particular model that fit a certain
           criteria as defined in the subclass's overriding method. Return True to skip saving, False to save"""
        False

    def deserialize_prep(self, **kwargs):
        """Users may override to manipulate the incoming object before calling save()"""
        pass

    def _deserialize_post(self, incoming_transaction):
        """Default behavior for all subclasses of this class is to
        serialize to outgoing transaction.

        Note: this is necessary because a deserialized object will not create
              an Outgoing Transaction by default since the "raw" parameter is True
              on deserialization."""
        OutgoingTransaction = get_model('sync', 'outgoingtransaction')
        try:
            OutgoingTransaction.objects.get(pk=incoming_transaction.id)
        except OutgoingTransaction.DoesNotExist:
            OutgoingTransaction.objects.create(
                pk=incoming_transaction.id,
                tx_name=incoming_transaction.tx_name,
                tx_pk=incoming_transaction.tx_pk,
                tx=incoming_transaction.tx,
                timestamp=incoming_transaction.timestamp,
                producer=incoming_transaction.producer,
                action=incoming_transaction.action)
        self.deserialize_post()

    def deserialize_post(self):
        """Users may override to do app specific tasks after deserialization."""
        pass

    def deserialize_on_duplicate(self):
        """Users may override this to determine how to handle a duplicate
        error on deserialization.

        If you have a way to help decide if a duplicate should overwrite
        the existing record or not, evaluate your criteria here and return
        True or False. If False is returned to the deserializer, the
        object will not be saved and the transaction WILL be flagged
        as consumed WITHOUT error.
        """
        return True

    def deserialize_get_missing_fk(self, attrname):
        """Override to return a foreignkey object for 'attrname',
        if possible, using criteria in self, otherwise return None"""
        raise ImproperlyConfigured('Method deserialize_get_missing_fk() must '
                                   'be overridden on model class {0}'.format(self._meta.object_name))

    def save_to_inspector(self, fields, instance_pk, using):
        """Override in concrete class."""
        return False

    class Meta:
        abstract = True
