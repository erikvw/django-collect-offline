from edc_sync.models.sync_model_mixin import SyncModelMixin
from edc_base.model.models import BaseUuidModel


class TestModel(SyncModelMixin, BaseUuidModel):

    class Meta:
        app_label = 'edc_sync'
