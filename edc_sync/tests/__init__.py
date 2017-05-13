from ..site_sync_models import site_sync_models
from ..sync_model import SyncModel

sync_models = ['edc_sync.testmodel',
               'edc_sync.badtestmodel',
               # 'edc_sync.m2m',
               'edc_sync.anotherbadtestmodel',
               'edc_sync.testmodelwithfkprotected',
               'edc_sync.testmodelwithm2m']
site_sync_models.register(sync_models, SyncModel)
