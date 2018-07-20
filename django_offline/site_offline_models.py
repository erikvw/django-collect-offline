from edc_base.site_models import SiteModels


class SiteSyncModelError(Exception):
    pass


class SiteOfflineModels(SiteModels):

    """ Main controller of :class:`offline_models` objects.
    """

    module_name = 'offline_models'
    register_historical = True

    @property
    def wrapper_cls(self):
        from .offline_model import OfflineModel
        return OfflineModel


site_offline_models = SiteOfflineModels()
