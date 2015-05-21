import socket

from django.core import serializers
from django.db import transaction
# from django.db.models.fields.related import ForeignKey, OneToOneField
# from django.db.utils import IntegrityError

from django_crypto_fields.classes import Cryptor

# from .. import transaction_producer
from django.core.serializers.base import DeserializationError


class TransactionMixin(object):

    aes_mode = 'local'
    use_encryption = True

    def deserialized_objects(self):
        if self.use_encryption:
            json_tx = Cryptor().aes_decrypt(self.tx, self.aes_mode)
        return serializers.deserialize("json", json_tx)
        # TODO: m2m_relation_dict is {m2m_field_name: list_of_related_objects}.

    def to_model_instance(self, to, check_hostname=None):
        if self.is_consumed:
            return True
        self.is_success = None
        self.destination = to
        self.check_hostname = check_hostname
        for obj in self.deserialized_objects():
            if self.ignore_obj(obj):
                pass
            elif self.action == 'I' or self.action == 'U':
                self.save_obj(obj)
            elif self.action == 'D':
                self.delete_obj(obj)
            else:
                raise DeserializationError('Unknown object action. Expected one of [I, U, D]. Got {}'.format(self.action))
        return self.is_consumed or self.is_ignored

    def ignore_obj(self, obj):
        """Returns True if this deserialized object is from the same DB
        that it is about to be saved to."""
        if not self.check_hostname:
            return False
        else:
            ignore = obj.object.hostname_modified == socket.gethostname()
            if ignore:
                self.is_ignored = True
                self.save(using=self.destination)
        return ignore

    def save_obj(self, obj):
        """Saves the deserialized object."""
        with transaction.atomic():
            self.pre_save_obj(obj)
            obj.save(using=self.destination)
            self.post_save_obj(obj)
        self.is_consumed = True
        self.save(using=self.destination)

    def pre_save_obj(self, obj):
        """Calls a method before saving the model instance, if it exists."""
        try:
            obj.object.deserialize_prep(using=self.destination)
        except AttributeError:
            pass

    def post_save_obj(self, obj):
        """Calls a method after saving the model instance, if it exists."""
        try:
            obj.object.deserialize_post(using=self.destination)
        except AttributeError:
            pass

    def delete_obj(self, obj):
        with transaction.atomic():
            obj.object.get(pk=obj.object.pk).delete()
        self.is_consumed = True
        self.save(using=self.destination)
