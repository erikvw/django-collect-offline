import socket

from django.apps import apps as django_apps
from django.conf import settings
from django.db.models.fields import UUIDField
from django_crypto_fields.constants import LOCAL_MODE
from django_crypto_fields.cryptor import Cryptor
from edc_utils import get_utcnow

from .constants import INSERT, UPDATE, DELETE
from .transaction import serialize


class OfflineNaturalKeyMissing(Exception):
    pass


class OfflineGetByNaturalKeyMissing(Exception):
    pass


class OfflineHistoricalManagerError(Exception):
    pass


class OfflineUuidPrimaryKeyMissing(Exception):
    pass


class OfflineModel:

    """A wrapper for offline model instances to add methods called in
    signals for synchronization.
    """

    def __init__(self, instance):
        try:
            self.is_serialized = settings.ALLOW_MODEL_SERIALIZATION
        except AttributeError:
            self.is_serialized = True
        self.instance = instance
        self.has_offline_historical_manager_or_raise()
        self.has_natural_key_or_raise()
        self.has_get_by_natural_key_or_raise()
        self.has_uuid_primary_key_or_raise()

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.instance)})"

    def __str__(self):
        return f"{self.instance._meta.label_lower}"

    def has_natural_key_or_raise(self):
        try:
            self.instance.natural_key
        except AttributeError:
            raise OfflineNaturalKeyMissing(
                f"Model '{self.instance._meta.app_label}.{self.instance._meta.model_name}' "
                "is missing method natural_key "
            )

    def has_get_by_natural_key_or_raise(self):
        try:
            self.instance.__class__.objects.get_by_natural_key
        except AttributeError:
            raise OfflineGetByNaturalKeyMissing(
                f"Model '{self.instance._meta.app_label}.{self.instance._meta.model_name}' "
                "is missing manager method get_by_natural_key "
            )

    def has_offline_historical_manager_or_raise(self):
        """Raises an exception if model uses a history manager and
        historical model history_id is not a UUIDField.

        Note: expected to use edc_model.HistoricalRecords instead of
        simple_history.HistoricalRecords.
        """
        try:
            model = self.instance.__class__.history.model
        except AttributeError:
            model = self.instance.__class__
        field = [field for field in model._meta.fields if field.name == "history_id"]
        if field and not isinstance(field[0], UUIDField):
            raise OfflineHistoricalManagerError(
                f"Field 'history_id' of historical model "
                f"'{model._meta.app_label}.{model._meta.model_name}' "
                "must be an UUIDfield. "
                "For history = HistoricalRecords() use edc_model.HistoricalRecords instead of "
                "simple_history.HistoricalRecords(). "
                f"See '{self.instance._meta.app_label}.{self.instance._meta.model_name}'."
            )

    def has_uuid_primary_key_or_raise(self):
        if self.primary_key_field.get_internal_type() != "UUIDField":
            raise OfflineUuidPrimaryKeyMissing(
                f"Expected Model '{self.instance._meta.label_lower}' "
                f"primary key {self.primary_key_field} to be a UUIDField "
                f"(e.g. AutoUUIDField). "
                f"Got {self.primary_key_field.get_internal_type()}."
            )

    @property
    def primary_key_field(self):
        """Return the primary key field.

        Is `id` in most cases. Is `history_id` for Historical models.
        """
        return [field for field in self.instance._meta.fields if field.primary_key][0]

    def to_outgoing_transaction(self, using, created=None, deleted=None):
        """ Serialize the model instance to an AES encrypted json object
        and saves the json object to the OutgoingTransaction model.
        """
        OutgoingTransaction = django_apps.get_model(
            "django_collect_offline", "OutgoingTransaction"
        )
        created = True if created is None else created
        action = INSERT if created else UPDATE
        timestamp_datetime = (
            self.instance.created if created else self.instance.modified
        )
        if not timestamp_datetime:
            timestamp_datetime = get_utcnow()
        if deleted:
            timestamp_datetime = get_utcnow()
            action = DELETE
        outgoing_transaction = None
        if self.is_serialized:
            hostname = socket.gethostname()
            outgoing_transaction = OutgoingTransaction.objects.using(using).create(
                tx_name=self.instance._meta.label_lower,
                tx_pk=getattr(self.instance, self.primary_key_field.name),
                tx=self.encrypted_json(),
                timestamp=timestamp_datetime.strftime("%Y%m%d%H%M%S%f"),
                producer=f"{hostname}-{using}",
                action=action,
                using=using,
            )
        return outgoing_transaction

    def encrypted_json(self):
        """Returns an encrypted json serialized from self.
        """
        json = serialize(objects=[self.instance])
        encrypted_json = Cryptor().aes_encrypt(json, LOCAL_MODE)
        return encrypted_json
