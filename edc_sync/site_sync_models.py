import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule

from .exceptions import AlreadyRegistered


class M:
    """Simple class to display models with sync attribute as True or False."""

    def __init__(self, app_label, model_name, is_sync_model=None):
        self.sync = is_sync_model
        self.app_label, self.model_name = app_label, model_name
        self.model = django_apps.get_model(app_label, model_name)
        self.verbose_name = self.model._meta.verbose_name

    def __repr__(self):
        return f'M({self.app_label}.{self.model_name}, sync={self.sync})'

    def __str__(self):
        return self.verbose_name


class SiteSyncModels:

    """ Main controller of :class:`sync_models` objects.
    """

    def __init__(self):
        self.registry = {}
        self.loaded = False

    def register(self, models, DefaultSyncModel):
        """Registers with app_label.modelname, SyncModel.
        """
        self.loaded = True
        for model in models:
            try:
                name, SyncModel = model
            except ValueError:
                name, SyncModel = model, DefaultSyncModel
            name = name.lower()
            if name not in self.registry:
                self.registry.update({name: SyncModel})
                self.registry.update(
                    {'.historical'.join(name.split('.')): SyncModel})
            else:
                raise AlreadyRegistered(
                    f'Model is already registered for synchronization. Got {name}.')

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

    def site_models(self, app_name=None, sync=None):
        """Returns a dictionary of registered models indicating if
        they are sync models or not.
        """
        sync = None if sync is None else sync
        site_models = {}
        for app_config in django_apps.get_app_configs():
            model_list = []
            for model in app_config.get_models():
                app_label, model_name = model._meta.label_lower.split('.')
                model_list.append(
                    M(app_label, model_name,
                      True if model._meta.label_lower in site_sync_models.registry else False))
            if model_list:
                model_list.sort(key=lambda x: x.verbose_name)
                site_models.update({app_label: model_list})
        if sync is True or sync is False:
            filtered_models = {}
            for app_label, model_list in site_models.items():
                model_list = [m for m in model_list if m.sync == sync]
                if model_list:
                    filtered_models.update({app_label: model_list})
            return filtered_models.get(app_name) if app_name else filtered_models
        else:
            return site_models.get(app_name) if app_name else site_models

    def autodiscover(self, module_name=None):
        """Autodiscovers classes in the sync_models.py file of
        any INSTALLED_APP.
        """
        module_name = module_name or 'sync_models'
        sys.stdout.write(' * checking for models to register ...\n')
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(
                        site_sync_models.registry)
                    import_module('{}.{}'.format(app, module_name))
                    sys.stdout.write(
                        f' * registered models from \'{app}\'.\n')
                except Exception as e:
                    if 'No module named \'{}.{}\''.format(app, module_name) not in str(e):
                        raise Exception(e)
                    site_sync_models.registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise
            except ImportError:
                pass


site_sync_models = SiteSyncModels()
