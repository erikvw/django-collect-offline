import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule
from builtins import AttributeError


class SiteSyncModelAlreadyRegistered(Exception):
    pass


class SiteSyncModelError(Exception):
    pass


class SiteSyncModelNotRegistered(Exception):
    pass


class M:
    """Simple class to display models with sync attribute as True or False."""

    def __init__(self, model=None):
        self.sync = True if model in site_sync_models.registry else False
        self.model = django_apps.get_model(*model.split('.'))
        self.verbose_name = self.model._meta.verbose_name

    def __repr__(self):
        return (f'{self.__class__.__name__}(model={self.model._meta.label_lower}, '
                f'sync={self.sync}))')

    def __str__(self):
        return f'{self.model._meta.label_lower}, sync={self.sync}'


class SiteSyncModels:

    """ Main controller of :class:`sync_models` objects.
    """

    def __init__(self):
        self.registry = {}
        self.loaded = False

    def register(self, models=None, sync_model_cls=None):
        """Registers with app_label.modelname, SyncModel.
        """
        self.loaded = True
        for model in models:
            try:
                name, SyncModel = model
            except ValueError:
                name, SyncModel = model, sync_model_cls
            name = name.lower()
            if name not in self.registry:
                self.registry.update({name: SyncModel})
                self.registry.update(
                    {'.historical'.join(name.split('.')): SyncModel})
            else:
                raise SiteSyncModelAlreadyRegistered(
                    f'Model is already registered for synchronization. Got {name}.')

    def get_as_sync_model(self, instance=None):
        """Returns a model instance wrapped with Sync methods.
        """
        try:
            sync_model_cls = self.registry.get(instance._meta.label_lower)
        except AttributeError as e:
            raise SiteSyncModelError(e)
        if sync_model_cls:
            wrapped_model = sync_model_cls(instance)
        else:
            raise SiteSyncModelNotRegistered(
                f'{repr(instance)} is not a registered sync model.')
        return wrapped_model

    def site_models(self, app_name=None, sync=None):
        """Returns a dictionary of registered models indicating if
        they are sync models or not.
        """
        site_models = {}
        for app_config in django_apps.get_app_configs():
            model_list = []
            for model in app_config.get_models():
                model_list.append(
                    M(model=model._meta.label_lower))
            if model_list:
                model_list.sort(key=lambda x: x.verbose_name)
                site_models.update({model._meta.app_label: model_list})
        if sync is not None:
            filtered_models = {}
            for app_label, model_list in site_models.items():
                model_list = [m for m in model_list if m.sync == sync]
                if model_list:
                    filtered_models.update({app_label: model_list})
            site_models = filtered_models.get(
                app_name) if app_name else filtered_models
        else:
            site_models = site_models.get(
                app_name) if app_name else site_models
        return site_models

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
