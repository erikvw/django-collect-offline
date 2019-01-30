import socket

from django.apps import apps as django_apps
from django_crypto_fields.constants import LOCAL_MODE
from django_crypto_fields.cryptor import Cryptor
from edc_device.constants import NODE_SERVER, CENTRAL_SERVER

from ..constants import DELETE
from .deserialize import deserialize


class TransactionDeserializerError(Exception):
    pass


def save(obj=None, m2m_data=None):
    """Saves a deserialized model object.

    Uses save_base to avoid running code in model.save() and
    to avoid triggering signals (if raw=True).
    """
    m2m_data = {} if m2m_data is None else m2m_data
    obj.save_base(raw=True)
    for attr, values in m2m_data.items():
        for value in values:
            getattr(obj, attr).add(value)


def aes_decrypt(cipher_text):
    return Cryptor().aes_decrypt(cipher_text, LOCAL_MODE)


class TransactionDeserializer:
    def __init__(self, using=None, allow_self=None, override_role=None, **kwargs):
        app_config = django_apps.get_app_config("edc_device")
        self.aes_decrypt = aes_decrypt
        self.deserialize = deserialize
        self.save = save
        self.allow_self = allow_self
        self.using = using
        if not app_config.is_server:
            if override_role not in [NODE_SERVER, CENTRAL_SERVER]:
                raise TransactionDeserializerError(
                    "Transactions may only be deserialized on a server. "
                    f"Got override_role={override_role}, device={app_config.device_id}, "
                    f"device_role={app_config.device_role}."
                )

    def deserialize_transactions(self, transactions=None, deserialize_only=None):
        """Deserializes the encrypted serialized model
        instances, tx, in a queryset of transactions.

        Note: each transaction instance contains encrypted JSON text
        that represents just ONE model instance.
        """

        if (
            not self.allow_self
            and transactions.filter(producer=socket.gethostname()).exists()
        ):
            raise TransactionDeserializerError(
                f"Not deserializing own transactions. Got "
                f"allow_self=False, hostname={socket.gethostname()}"
            )
        for transaction in transactions:
            json_text = self.aes_decrypt(cipher_text=transaction.tx)
            json_text = self.custom_parser(json_text)
            deserialized = next(self.deserialize(json_text=json_text))
            if not deserialize_only:
                if transaction.action == DELETE:
                    deserialized.object.delete()
                else:
                    self.save(obj=deserialized.object, m2m_data=deserialized.m2m_data)
                transaction.is_consumed = True
                transaction.save()

    def custom_parser(self, json_text=None):
        """Runs json_text thru custom parsers.
        """
        app_config = django_apps.get_app_config("django_collect_offline")
        for json_parser in app_config.custom_json_parsers:
            json_text = json_parser(json_text)
        return json_text
