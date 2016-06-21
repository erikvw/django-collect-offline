from base64 import b64encode, b64decode

from django.utils import six
from django.utils.encoding import force_bytes
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.fields import Field
from rest_framework.fields import empty

from edc_sync.choices import ACTIONS
from edc_sync.models import IncomingTransaction, OutgoingTransaction


class BinaryField(Field):
    default_error_messages = {
        'invalid': _('Value must be valid Binary.')
    }

    def to_internal_value(self, data):
        if isinstance(data, six.text_type):
            return six.memoryview(b64decode(force_bytes(data))).tobytes()
        return data

    def to_representation(self, value):
        if isinstance(value, six.binary_type):
            return b64encode(force_bytes(value)).decode('ascii')
        return value

    def run_validation(self, data=empty):
        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data
        value = self.to_internal_value(data)
        self.run_validators(value)
        return value


class BaseModelSerializer:

    model_cls = None

    user_created = serializers.CharField(
        max_length=50,
        allow_blank=True)

    user_modified = serializers.CharField(
        max_length=50,
        allow_blank=True)

    hostname_created = serializers.CharField(
        max_length=50,
        allow_blank=True)

    hostname_modified = serializers.CharField(
        max_length=50,
        allow_blank=True)

    revision = serializers.CharField(
        max_length=75)

    def create(self, validated_data):
        return self.model_cls.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for fieldname in [fld.name for fld in self.model._meta.fields]:
            setattr(instance, fieldname, validated_data.get(fieldname, getattr(instance, fieldname)))
        instance.save()
        return instance


class BaseTransactionSerializer(BaseModelSerializer, serializers.Serializer):

    pk = serializers.UUIDField(read_only=True)

    tx = BinaryField()

    tx_name = serializers.CharField(
        max_length=64)

    tx_pk = serializers.UUIDField()

    producer = serializers.CharField(max_length=200)

    action = serializers.ChoiceField(
        choices=ACTIONS)

    timestamp = serializers.CharField(
        max_length=50)

    consumed_datetime = serializers.DateTimeField(
        allow_null=True,
        default=None)

    consumer = serializers.CharField(
        max_length=200,
        allow_null=True,
        allow_blank=True)

    is_ignored = serializers.BooleanField(
        default=False)

    is_error = serializers.BooleanField(
        default=False)

    error = serializers.CharField(
        max_length=1000,
        allow_null=True,
        allow_blank=True)


class IncomingTransactionSerializer(BaseTransactionSerializer):

    model_class = IncomingTransaction


class OutgoingTransactionSerializer(BaseTransactionSerializer):

    model_class = OutgoingTransaction
