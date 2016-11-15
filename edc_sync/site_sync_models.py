import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule

from .exceptions import AlreadyRegistered


class SiteSyncModels:

    """ Main controller of :class:`sync_models` objects."""

    def __init__(self):
        self.registry = {}
        self.loaded = False

    def register(self, models, DefaultSyncModel):
        """Registers with app_label.modelname, SyncModel."""
        self.loaded = True
        for model in models:
            try:
                name, SyncModel = model
            except ValueError:
                name, SyncModel = model, DefaultSyncModel
            name = name.lower()
            if name not in self.registry:
                self.registry.update({name: SyncModel})
                self.registry.update({'.historical'.join(name.split('.')): SyncModel})
            else:
                raise AlreadyRegistered('Model is already registered for synchronization. Got {}.'.format(name))

    def get_as_sync_model(self, instance):
        """Returns a model instance wrapped with Sync methods."""
        SyncModel = self.registry.get(instance._meta.label_lower)
        try:
            sync_model = SyncModel(instance)
        except TypeError as e:
            if '\'NoneType\' object is not callable' not in str(e):
                raise TypeError(e)
            sync_model = None
        return sync_model

    def autodiscover(self, module_name=None):
        """Autodiscovers classes in the sync_models.py file of any INSTALLED_APP."""
        module_name = module_name or 'sync_models'
        sys.stdout.write(' * checking for models to register ...\n')
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_sync_models.registry)
                    import_module('{}.{}'.format(app, module_name))
                    sys.stdout.write(' * registered models from \'{}\'.\n'.format(app))
                except Exception as e:
                    if 'No module named \'{}.{}\''.format(app, module_name) not in str(e):
                        raise Exception(e)
                    site_sync_models.registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise
            except ImportError:
                pass

site_sync_models = SiteSyncModels()
