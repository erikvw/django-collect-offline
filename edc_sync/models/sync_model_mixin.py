import socket

from django.conf import settings
from django.core import serializers
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.fields import UUIDField, AutoField
from django.utils import timezone
from django.utils.timezone import now
from simple_history.models import HistoricalRecords

from django_crypto_fields.constants import LOCAL_MODE
from django_crypto_fields.cryptor import Cryptor

from ..exceptions import SyncModelError

from .outgoing_transaction import OutgoingTransaction


class SyncMixin:

    """Base model for all UUID models and adds synchronization
    methods and signals. """

    @property
    def primary_key_field(self):
        """Return the primary key field.

        Is `id` in most cases. Is `history_id` for Historical models."""
        try:
            field = [field for field in self._meta.fields if field.primary_key][0]
        except IndexError:
            field = None
        return field

    def to_outgoing_transaction(self, using, created=None, deleted=None):
        """ Serialize the model instance to an AES encrypted json object
        and saves the json object to the OutgoingTransaction model."""

        # TODO: i think using should always be default

        created = True if created is None else created
        action = 'I' if created else 'U'
        if deleted:
            action = 'D'
        outgoing_transaction = None
        if self.is_serialized():
            hostname = socket.gethostname()
            outgoing_transaction = OutgoingTransaction.objects.using(using).create(
                tx_name='{}.{}'.format(self._meta.app_label, self._meta.object_name.lower()),
                tx_pk=getattr(self, self.primary_key_field.name),
                tx=self.encrypted_json(),
                timestamp=timezone.now().strftime('%Y%m%d%H%M%S%f'),
                producer='{}-{}'.format(hostname, using),
                action=action,
                using=using)
        return outgoing_transaction

    def is_serialized(self):
        """Return the value of the settings.ALLOW_MODEL_SERIALIZATION or True.

        If True, this instance will serialized and saved to OutgoingTransaction.
        """
        try:
            is_serialized = settings.ALLOW_MODEL_SERIALIZATION
        except AttributeError:
            is_serialized = True
        return is_serialized

    def encrypted_json(self):
        """Returns an encrypted json serialized from self."""
        json = serializers.serialize(
            "json", [self, ], ensure_ascii=True, use_natural_foreign_keys=True)
        encrypted_json = Cryptor().aes_encrypt(json, LOCAL_MODE)
        return encrypted_json

    def skip_saving_criteria(self):
        """Returns True to skip saving, False to save (default).

        Users may override to avoid saving/persisting instances of a particular model that fit a certain
           criteria as defined in the subclass's overriding method.

        If there you want a certain model to not be persisted for what ever reason,
        (Usually to deal with temporary data cleaning issues) then define the method skip_saving_criteria()
        in your model which return True/False based on the criteria to be used for skipping.
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
        if possible, using criteria in self, otherwise return None"""
        raise ImproperlyConfigured('Method deserialize_get_missing_fk() must '
                                   'be overridden on model class {0}'.format(self._meta.object_name))


class SyncHistoricalRecords(HistoricalRecords):

    """Sync HistoricalRecords that uses a UUID primary key and has a natural key method."""

    def get_history_id_field(self, model):
        """Return a field instance without initially assuming
        it should be AutoField.

        For example, primary key is UUIDField(primary_key=True, default=uuid.uuid4)"""
        try:
            field = [field for field in model._meta.fields if field.primary_key][0]
            field = field.__class__(primary_key=True, default=field.default)
        except (IndexError, TypeError):
            field = AutoField(primary_key=True)
        return field

    def get_extra_fields(self, model, fields):
        """Override to set history_id (to UUIDField) and add the
        SyncModelMixin methods."""
        extra_fields = super(SyncHistoricalRecords, self).get_extra_fields(model, fields)
        extra_fields.update({'history_id': self.get_history_id_field(model)})
        extra_fields.update(
            {attr: getattr(SyncMixin, attr)
             for attr in [attr for attr in dir(SyncMixin)if not attr.startswith('_')]
             })
        return extra_fields

    def post_save(self, instance, created, **kwargs):
        """Override to include \'using\'."""
        if not created and hasattr(instance, 'skip_history_when_saving'):
            return
        if not kwargs.get('raw', False):
            self.create_historical_record(instance, created and '+' or '~', using=kwargs.get('using'))

    def post_delete(self, instance, **kwargs):
        """Override to include \'using\'."""
        self.create_historical_record(instance, '-', using=kwargs.get('using'))

    def create_historical_record(self, instance, history_type, **kwargs):
        """Override to include \'using\'."""
        history_date = getattr(instance, '_history_date', now())
        history_user = self.get_history_user(instance)
        manager = getattr(instance, self.manager_name)
        attrs = {}
        for field in instance._meta.fields:
            attrs[field.attname] = getattr(instance, field.attname)
        manager.using(kwargs.get('using')).create(history_date=history_date, history_type=history_type,
                                                  history_user=history_user, **attrs)


class SyncModelMixin(SyncMixin, models.Model):

    def __init__(self, *args, **kwargs):
        try:
            self.natural_key
        except AttributeError:
            raise SyncModelError('Model \'{}.{}\' is missing method natural_key '.format(
                self._meta.app_label, self._meta.model_name))
        try:
            self.__class__.objects.get_by_natural_key
        except AttributeError:
            raise SyncModelError('Model \'{}.{}\' is missing manager method get_by_natural_key '.format(
                self._meta.app_label, self._meta.model_name))
        try:
            # if using history manager, historical model history_id (primary_key) must be UUIDField.
            historical_model = self.__class__.history.model
            field = [field for field in historical_model._meta.fields if field.name == 'history_id'][0]
            if not isinstance(field, UUIDField):
                raise SyncModelError(
                    'Field \'history_id\' of historical model \'{}.{}\' must be an UUIDfield. '
                    'Use history = SyncHistoricalRecords() instead of history = HistoricalRecords(). '
                    'See \'{}.{}\'.'.format(
                        historical_model._meta.app_label, historical_model._meta.model_name,
                        self._meta.app_label, self._meta.model_name))
        except AttributeError:
            pass
        if self.primary_key_field.get_internal_type() != 'UUIDField':
            raise SyncModelError(
                'Expected Model \'{}.{}\' primary key to be a UUIDField (e.g. AutoUUIDField). Got {}.'.format(
                    self._meta.app_label, self._meta.model_name, self.primary_key_field.get_internal_type()))
        super(SyncModelMixin, self).__init__(*args, **kwargs)

    class Meta:
        abstract = True
