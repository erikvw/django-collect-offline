import socket

from django.apps import apps as django_apps
from django.core import serializers
from django.db import transaction
from django_crypto_fields.constants import LOCAL_MODE
from django_crypto_fields.cryptor import Cryptor

from .constants import DELETE


class TransactionDeserializerError(Exception):
    pass


def deserialize(json_text=None):
    """Wraps django deserialize with defaults for JSON
    and natural keys.
    """
    return serializers.deserialize(
        "json", json_text,
        ensure_ascii=True,
        use_natural_foreign_keys=True,
        use_natural_primary_keys=False)


def save(obj=None, m2m_data=None, raw=None):
    """Saves a deserialized model object.

    Uses save_base to avoid running code in model.save() and
    to avoid triggering signals (if raw=True).
    """
    m2m_data = {} if m2m_data is None else m2m_data
    obj.save_base(raw=raw)
    for attr, values in m2m_data.items():
        for value in values:
            getattr(obj, attr).add(value)


def aes_decrypt(cipher_text):
    return Cryptor().aes_decrypt(cipher_text, LOCAL_MODE)


class TransactionDeserializer:

    def __init__(self, using=None, allow_self=None, allow_any_role=None, raw=None):
        edc_device_app_config = django_apps.get_app_config('edc_device')
        self.aes_decrypt = aes_decrypt
        self.deserialize = deserialize
        self.save = save
        self.raw = True if raw is None else raw
        self.allow_self = allow_self
        self.using = using
        if not allow_any_role and not edc_device_app_config.is_server:
            raise TransactionDeserializerError(
                f'Transactions may only be deserialized on a server. '
                f'Got allow_any_role=False, device={edc_device_app_config.device_id}, '
                f'device_role={edc_device_app_config.role}.')

    def deserialize_transactions(self, transactions=None, deserialize_only=None):
        """Deserializes the encrypted serialized model instances, tx, in a queryset
        of transactions.

        Note: each transaction instance contains encrypted JSON text
        that represents just ONE model instance.
        """
        if not self.allow_self and transactions.filter(
                producer=socket.gethostname()).exists():
            raise TransactionDeserializerError(
                f'Not deserializing own transactions. Got '
                f'allow_self=False, hostname={socket.gethostname()}')
        for transaction in transactions:
            json_text = self.aes_decrypt(cipher_text=transaction.tx)
            deserialized = next(self.deserialize(json_text=json_text))
            if not deserialize_only:
                if transaction.action == DELETE:
                    deserialized.object.delete()
                else:
                    self.save(
                        obj=deserialized.object,
                        m2m_data=deserialized.m2m_data,
                        raw=self.raw)
                transaction.is_consumed = True
                transaction.save()
