import socket
import sys

from django.core import serializers
from django.db import models, transaction
from django.db.models import get_model
from django.db.models.fields.related import OneToOneField, ForeignKey
from django.db.utils import IntegrityError
from django.utils import timezone

from edc_base.encrypted_fields import FieldCryptor

from ..exceptions import SyncError

from .base_transaction import BaseTransaction
from .incoming_transaction_manager import IncomingTransactionManager
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

    def deserialize_transaction(self, using, check_hostname=None):
        inserted, updated, deleted = 0, 0, 0
        check_hostname = True if check_hostname is None else check_hostname
        decrypted_transaction = FieldCryptor('aes', 'local').decrypt(self.tx)
        for obj in serializers.deserialize("json", decrypted_transaction):
            if self.action == 'D':
                deleted = self.deserialize_delete_tx(obj, using, check_hostname)
            elif self.action == 'I':
                inserted = self.deserialize_insert_tx(obj, using, check_hostname)
            elif self.action == 'U':
                updated = self.deserialize_update_tx(obj, using, check_hostname)
            else:
                raise SyncError('Unexpected value for action. Got {}'.format(self.action))
            if any([inserted, deleted, updated]):
                self.is_ignored = False
                self.is_consumed = True
                self.consumed_datetime = timezone.now()
                self.consumer = transaction_producer
                self.save(using=using)
        return inserted, updated, deleted

    def deserialize_insert_tx(self, obj, using, check_hostname=None, verbose=None):
        return self.deserialize_update_tx(obj, using, check_hostname, verbose)

    def deserialize_delete_tx(self, obj, using, check_hostname=None):
        # obj.object.deserialize_prep(action='D')
        count = 0
        check_hostname = True if check_hostname is None else check_hostname
        if obj.object.hostname_modified == socket.gethostname() and check_hostname:
            raise SyncError('Incoming transactions exist that are from this host.')
        else:
            with transaction.atomic(using=using):
                self.is_ignored = False
                self.is_consumed = True
                self.consumer = transaction_producer
                self.save(using=using)
                count = 1
        return count

    def deserialize_update_tx(self, obj, using, check_hostname=None, verbose=None):
        count = 0
        check_hostname = True if check_hostname is None else check_hostname
        if obj.object.hostname_modified == socket.gethostname() and check_hostname:
            raise SyncError('Incoming transactions exist that are from this host.')
        else:
            with transaction.atomic(using):
                obj.save(using=using)
                count = 1
        return count

#     def ignore_own_transaction(self):
#         """ Ignores own transactions by marking them as is_ignored=True."""
#         print('    skipping - not consuming own transactions (using={0})'.format(self.using))
#         self.is_ignored = True
#         self.save()
#         return True

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
        ordering = ['timestamp', 'producer']
