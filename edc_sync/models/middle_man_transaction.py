from datetime import datetime

from django.db import models
from django.apps import apps
from django.conf import settings

from edc_device.device import Device

from ..mixins import TransactionMixin

from . import BaseTransaction


class MiddleManTransaction(BaseTransaction, TransactionMixin):

    """ transactions produced locally to be consumed/sent to a queue or consumer """

    is_consumed_middleman = models.BooleanField(
        default=False,
        db_index=True,
    )

    is_consumed_server = models.BooleanField(
        default=False,
        db_index=True,
    )

    def save(self, *args, **kwargs):
        if self.is_consumed_server and not self.consumed_datetime:
            self.consumed_datetime = datetime.today()
        if not Device().is_middleman:
            raise TypeError('\'{0}\' is not configured to be a MiddleMan, so you cannot save MiddleMan transanctions here.'.format(settings.DEVICE_ID))
        super(MiddleManTransaction, self).save(*args, **kwargs)

    def deserialize_to_inspector_on_post_save(self, instance, raw, created, using, **kwargs):
        instance.to_model_instance(using)
        # model_dict = DeserializeFromTransaction().decrypt_transanction(self)[0]
        tokens = model_dict.get('model').split('.')
        # app_name = tokens[0]
        app_name = instance._meta.app_name
        # model_name = tokens[1]
        model_name = instance._meta.object_name
        model = apps.get_model(app_name, model_name)
        if model and 'save_to_inspector' in dir(model):
            fields = model_dict.get('fields')
            instance_pk = model_dict.get('pk')
            model().save_to_inspector(fields, instance.pk, using)

    objects = models.Manager()

    class Meta:
        app_label = 'edc_sync'
        ordering = ['timestamp']
