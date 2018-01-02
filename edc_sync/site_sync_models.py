from edc_base.site_models import SiteModels


class SiteSyncModelError(Exception):
    pass


class SiteSyncModels(SiteModels):

    """ Main controller of :class:`sync_models` objects.
    """

    module_name = 'sync_models'
    register_historical = True

    @property
    def wrapper_cls(self):
        from .sync_model import SyncModel
        return SyncModel


site_sync_models = SiteSyncModels()
