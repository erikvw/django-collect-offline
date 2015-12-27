import socket
import sys

from datetime import datetime

from django.core import serializers
from django.db import models, transaction, connection
from django.db.models import get_model
from django.db.models.fields.related import OneToOneField, ForeignKey
from django.db.utils import IntegrityError

from edc_base.encrypted_fields import FieldCryptor

from ..exceptions import SyncError
from ..managers import IncomingTransactionManager

from .base_transaction import BaseTransaction
from .transaction_producer import transaction_producer


class IncomingTransaction(BaseTransaction):
    """ Transactions received from a remote producer and to be consumed locally. """

    check_hostname = None

    is_consumed = models.BooleanField(
        default=False,
        db_index=True)

    is_self = models.BooleanField(
        default=False,
        db_index=True)

    objects = IncomingTransactionManager()

    def save(self, *args, **kwargs):
        if self.hostname_modified == socket.gethostname():
            self.is_self = True  # FIXME: is this needed?
        if self.is_consumed and not self.consumed_datetime:
            self.consumed_datetime = datetime.today()
        super(IncomingTransaction, self).save(*args, **kwargs)

    def deserialize_transaction(self, check_hostname=None):
        is_success = False
        self.check_hostname = True if check_hostname is None else check_hostname
        decrypted_transaction = FieldCryptor('aes', 'local').decrypt(self.tx)
        for obj in serializers.deserialize("json", decrypted_transaction):
            if self.action == 'D':
                is_success = self.deserialize_delete_tx(obj)
            elif self.action == 'I':
                is_success = self.deserialize_update_tx(obj)
            elif self.action == 'U':
                is_success = self.deserialize_update_tx(obj)
            else:
                raise SyncError('Unexpected value for action. Got {}'.format(self.action))
        return is_success

    def deserialize_delete_tx(self, obj):
        # If the transactions is a DELETE then let the model itself deal with how
        # it handles this action by overiding method deserialize_prep() in the model.
        obj.object.deserialize_prep(action='D')
        self.is_ignored = False
        self.is_consumed = True
        self.consumer = transaction_producer
        self.save()
        is_success = True
        return is_success

    def deserialize_update_tx(self, obj):
        print('    {0}'.format(obj.object._meta.object_name))
        if obj.object.hostname_modified == socket.gethostname() and self.check_hostname:
            is_success = self.ignore_own_transaction()
        else:
            self.is_ignored = False
            is_success = False
            obj.object.deserialize_prep()
            try:
                with transaction.atomic():
                    obj.save()
                    msg = '    OK - normal save'
                is_success = True
            except IntegrityError as exception:
                if 'Cannot add or update a child row' in str(exception):
                    is_success = self.retry_on_cannot_add_or_update_child_row(obj, exception)
                elif 'Duplicate' in str(exception):
                    is_success = self.retry_on_duplicate(obj, exception)
                else:
                    print('    {0}'.format(exception))
                    raise IntegrityError(exception)
            except:
                print(connection.queries)
                print("        [b] Unexpected error:", sys.exc_info())
                raise
            obj.object._deserialize_post(self)
            print(msg)
            if is_success:
                self.is_consumed = True
                self.consumer = transaction_producer
                self.save()

    def ignore_own_transaction(self):
        # ignore your own transactions and mark them as is_ignored=True
        print('    skipping - not consuming my own transactions (using={0})'.format(self.using))
        self.is_ignored = True
        self.save()
        return True

    def retry_on_cannot_add_or_update_child_row(self, obj, exception):
        if 'audit' in obj.object._meta.db_table:
            # TODO: now that audit uses natural keys, saving should
            # no longer raise an Integrity Error once all old
            # transactions are processed - erikvw 20140930
            print('    try again from \'cannot add or update a child row\'')
            audited_model_cls = get_model(
                obj.object._meta.app_label,
                obj.object._meta.model_name.replace('audit', ''))
            # try:
            audited_obj = audited_model_cls.objects.get(pk=obj.object._audit_id)
            for field in obj.object._meta.fields:
                if isinstance(field, (OneToOneField, ForeignKey)):
                    # it is OK to just set the fk to None on audit tables
                    setattr(obj.object, field.name, getattr(audited_obj, field.name))
            obj.save(using=self.using)
            # except audited_model_cls.DoesNotExist:
            #    pass
        else:
            foreign_key_error = []
            for field in obj.object._meta.fields:
                if isinstance(field, ForeignKey):
                    try:
                        getattr(obj.object, field.name)
                    except AttributeError:
                        print('    unable to getattr {0}'.format(field.name))
                        foreign_key_error.append(field)
            for field in foreign_key_error:
                print('    deserialize_get_missing_fk on model {0} for field {1} on using={2}'.format(
                    obj.object._meta.object_name, field.name, self.using))
                setattr(obj.object, field.name, obj.object.deserialize_get_missing_fk(field.name))
            try:
                obj.save(using=self.using)
                obj.object._deserialize_post(self)
                print('   OK saved after integrity error on using={0}'.format(self.using))
                is_success = True
            except Exception as e:
                print(e)
                self.is_ignored = True
        return is_success

    def retry_on_duplicate(self, obj):
        # if the integrity error refers to a duplicate
        # check the unique_together meta class value to attempt to
        # locate the existing pk.
        # If pk found, overwrite the pk in the json with the existing pk.
        # Try to save again
        print('    duplicate on {0}'.format(self.using))
        if not obj.object._meta.unique_together:
            # if there is no other constraint on the model
            # then an integrity error does not really make sense.
            # but anyway ...
            print('   missing unique_together attribute')
            raise
        options = {}
        for tpl in obj.object._meta.unique_together:
            for f in tpl:
                options.update({f: getattr(obj.object, f)})
            if not obj.object.__class__.objects.filter(**options).exists():
                # it should exist, otherwise how did we get an integrity error?
                print('   not found using unique_together field atttributes')
                raise
            else:
                old_pk = obj.object.id
                new_pk = obj.object.__class__.objects.get(**options).pk
                obj.object.id = new_pk
                try:
                    print('    deserialize_on_duplicate')
                    if 'deserialize_on_duplicate' in dir(obj.object) and obj.object.deserialize_on_duplicate():
                        print('    deserialize_on_duplicate')
                        # obj.object.deserialize_on_duplicate()
                        # not every duplicate needs to be saved
                        # if you can develop criteria to decide,
                        # then use deserialize_on_duplicate to evaluate
                        print('    try save again')
                        obj.save(using=self.using)
                        obj.object._deserialize_post(self)
                        is_success = True
                        # change all pk to the new pk for is_consumed=False.
                        print('    OK saved, now replace_pk_in_tx on using={0}'.format(self.using))
                        self.__class__.objects.replace_pk_in_tx(old_pk, new_pk, self.using)
                        print('    {0} is now {1}'.format(old_pk, new_pk))
                    else:
                        print('    no deserialize_on_duplicate method/model choosing to ignore duplicate')
                        self.is_ignored = True
                        self.is_error = True
                        self.save(using=self.using)
                except IntegrityError as error:
                    print('    integrity error ... giving up.')
                    self.is_consumed = False
                    self.consumer = None
                    self.is_error = True
                    self.error = error
                    self.save(using=self.using)
                except Exception as e:
                    print("        [a] Unexpected error:", sys.exc_info()[0])
                    raise Exception(e)
        return is_success

    class Meta:
        app_label = 'edc_sync'
        # db_table = 'bhp_sync_incomingtransaction'
        ordering = ['timestamp']
