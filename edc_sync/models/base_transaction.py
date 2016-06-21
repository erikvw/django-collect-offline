from django.core.urlresolvers import reverse
from django.db import models

from edc_base.model.models import BaseUuidModel


class BaseTransaction(BaseUuidModel):

    tx = models.BinaryField()

    tx_name = models.CharField(
        max_length=64,
        db_index=True)

    tx_pk = models.UUIDField(
        db_index=True)

    producer = models.CharField(
        max_length=200,
        db_index=True,
        help_text='Producer name')

    action = models.CharField(
        max_length=1,
        choices=(('I', 'Insert'), ('U', 'Update'), ('D', 'Delete')))

    timestamp = models.CharField(
        max_length=50,
        db_index=True)

    consumed_datetime = models.DateTimeField(
        null=True,
        blank=True)

    consumer = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        db_index=True)

    is_ignored = models.BooleanField(
        default=False,
        db_index=True,
    )

    is_error = models.BooleanField(
        default=False,
        db_index=True)

    error = models.TextField(
        max_length=1000,
        null=True,
        blank=True)

    batch_seq = models.IntegerField(null=True, blank=True)

    batch_id = models.IntegerField(null=True, blank=True)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.tx_name)

    def __str__(self):
        return '</{}.{}/{}/{}/{}/>'.format(self._meta.app_label, self._meta.model_name, self.id, self.tx_name, self.action)
        # return '{0} {1} {2}'.format(self.tx_name, self.producer, self.action)

    def save(self, *args, **kwargs):
        try:
            print(str(self))
            self.tx = self.tx.encode()
        except AttributeError:
            pass
        super(BaseTransaction, self).save(*args, **kwargs)

    def render(self):
        url = reverse('render_url',
                      kwargs={
                          'model_name': self._meta.object_name.lower(),
                          'pk': self.pk})
        ret = ('<a href="{url}" class="add-another" id="add_id_report" '
               'onclick="return showAddAnotherPopup(this);"> <img src="/static/admin/img/icon_addlink.gif" '
               'width="10" height="10" alt="View"/></a>'.format(url=url))
        return ret
    render.allow_tags = True

    class Meta:
        abstract = True
