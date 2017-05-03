import socket

from django.apps import apps as django_apps
from django.conf import settings
from django.core import serializers
from django.core.exceptions import ImproperlyConfigured
from django.db.models.fields import UUIDField
from django_crypto_fields.constants import LOCAL_MODE
from django_crypto_fields.cryptor import Cryptor

from edc_base.utils import get_utcnow

from .exceptions import SyncModelError


class SyncModel:

    """A wrapper for instances to add methods called in
    edc_sync.signals for synchronization.
    """

    def __init__(self, instance):
        try:
            self.is_serialized = settings.ALLOW_MODEL_SERIALIZATION
        except AttributeError:
            self.is_serialized = True
        self.instance = instance
        try:
            self.instance.natural_key
        except AttributeError:
            raise SyncModelError(
                f'Model \'{self.instance._meta.app_label}.{self.instance._meta.model_name}\' '
                'is missing method natural_key ')
        try:
            self.instance.__class__.objects.get_by_natural_key
        except AttributeError:
            raise SyncModelError(
                f'Model \'{self.instance._meta.app_label}.{self.instance._meta.model_name}\' '
                'is missing manager method get_by_natural_key ')
        try:
            # if using history manager, historical model history_id
            # (primary_key) must be UUIDField.
            historical_model = self.instance.__class__.history.model
            field = [
                field for field in historical_model._meta.fields if field.name == 'history_id'][0]
            if not isinstance(field, UUIDField):
                raise SyncModelError(
                    'Field \'history_id\' of historical model \'{}.{}\' must be an UUIDfield. '
                    'For history = HistoricalRecords() use edc_base.HistoricalRecords instead of '
                    'simple_history.HistoricalRecords(). '
                    'See \'{}.{}\'.'.format(
                        historical_model._meta.app_label, historical_model._meta.model_name,
                        self.instance._meta.app_label, self.instance._meta.model_name))
        except AttributeError:
            pass
        if self.primary_key_field.get_internal_type() != 'UUIDField':
            raise SyncModelError(
                'Expected Model \'{}.{}\' primary key {} to be a UUIDField (e.g. AutoUUIDField). Got {}.'.format(
                    self.instance._meta.app_label, self.instance._meta.model_name,
                    self.primary_key_field, self.primary_key_field.get_internal_type()))

    def __str__(self):
        return '{}'.format(self.instance._meta.label_lower)

    @property
    def primary_key_field(self):
        """Return the primary key field.

        Is `id` in most cases. Is `history_id` for Historical models.
        """
        try:
            field = [
                field for field in self.instance._meta.fields if field.primary_key][0]
        except IndexError:
            field = None
        return field

    def to_outgoing_transaction(self, using, created=None, deleted=None):
        """ Serialize the model instance to an AES encrypted json object
        and saves the json object to the OutgoingTransaction model.
        """
        OutgoingTransaction = django_apps.get_model(
            'edc_sync', 'OutgoingTransaction')
        created = True if created is None else created
        action = 'I' if created else 'U'
        timestamp_datetime = self.instance.created if created else self.instance.modified
        if not timestamp_datetime:
            timestamp_datetime = get_utcnow()
        if deleted:
            action = 'D'
        outgoing_transaction = None
        if self.is_serialized:
            hostname = socket.gethostname()
            outgoing_transaction = OutgoingTransaction.objects.using(using).create(
                tx_name=self.instance._meta.label_lower,
                tx_pk=getattr(self.instance, self.primary_key_field.name),
                tx=self.encrypted_json(),
                timestamp=timestamp_datetime.strftime('%Y%m%d%H%M%S%f'),
                producer='{}-{}'.format(hostname, using),
                action=action,
                using=using)
        return outgoing_transaction

    def encrypted_json(self):
        """Returns an encrypted json serialized from self.
        """
        json = serializers.serialize(
            "json", [self.instance, ], ensure_ascii=True,
            use_natural_foreign_keys=True)
        encrypted_json = Cryptor().aes_encrypt(json, LOCAL_MODE)
        return encrypted_json

    def skip_saving_criteria(self):
        """Returns True to skip saving, False to save (default).

        Users may override to avoid saving/persisting instances of a
        particular model that fit a certain criteria as defined in
        the subclass's overriding method.

        If there you want a certain model to not be persisted for
        what ever reason, (Usually to deal with temporary data
        cleaning issues) then define the method skip_saving_criteria()
        in your model which return True/False based on the criteria
        to be used for skipping.
        """
        False

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
        if possible, using criteria in self, otherwise return None.
        """
        raise ImproperlyConfigured(
            f'Method deserialize_get_missing_fk() must '
            f'be overridden on model class {self._meta.object_name}')
