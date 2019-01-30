import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule


class SiteModelAlreadyRegistered(Exception):
    pass


class SiteModelError(Exception):
    pass


class SiteModelNotRegistered(Exception):
    pass


class SiteSyncModelError(Exception):
    pass


class SiteModels:

    wrapper_cls = None
    register_historical = True

    def __init__(self):
        self.registry = {}
        self.loaded = False

    def register(self, models=None, wrapper_cls=None):
        """Registers with app_label.modelname, wrapper_cls.
        """
        self.loaded = True
        for model in models:
            model = model.lower()
            if model not in self.registry:
                self.registry.update({model: wrapper_cls or self.wrapper_cls})
                if self.register_historical:
                    historical_model = ".historical".join(model.split("."))
                    self.registry.update(
                        {historical_model: wrapper_cls or self.wrapper_cls}
                    )
            else:
                raise SiteModelAlreadyRegistered(
                    f"Model is already registered. Got {model}."
                )

    def register_for_app(
        self, app_label=None, exclude_models=None, include_list_models=None
    ):
        """Registers all models for this app_label.
        """
        from edc_list_data.model_mixins import ListModelMixin

        models = []
        exclude_models = exclude_models or []
        app_config = django_apps.get_app_config(app_label)
        for model in app_config.get_models():
            if model._meta.label_lower in exclude_models:
                pass
            elif include_list_models and issubclass(model, ListModelMixin):
                models.append(model._meta.label_lower)
            else:
                models.append(model._meta.label_lower)
        self.register(models)

    def get_wrapped_instance(self, instance=None):
        """Returns a wrapped model instance.
        """
        if instance._meta.label_lower not in self.registry:
            raise SiteModelNotRegistered(
                f"{repr(instance)} is not registered with {self}."
            )
        wrapper_cls = self.registry.get(instance._meta.label_lower) or self.wrapper_cls
        if wrapper_cls:
            return wrapper_cls(instance)
        return instance

    def site_models(self, app_label=None):
        """Returns a dictionary of registered models.
        """
        site_models = {}
        app_configs = (
            django_apps.get_app_configs()
            if app_label is None
            else [django_apps.get_app_config(app_label)]
        )
        for app_config in app_configs:
            model_list = [
                model
                for model in app_config.get_models()
                if model._meta.label_lower in self.registry
            ]
            if model_list:
                model_list.sort(key=lambda m: m._meta.verbose_name)
                site_models.update({app_config.name: model_list})
        return site_models

    def autodiscover(self, module_name=None):
        module_name = module_name or self.module_name
        sys.stdout.write(" * checking for models to register ...\n")
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.deepcopy(self.registry)
                    import_module(f"{app}.{module_name}")
                    sys.stdout.write(f" * registered models from '{app}'.\n")
                except Exception as e:
                    if f"No module named '{app}.{module_name}'" not in str(e):
                        raise
                    self.registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise
            except ImportError:
                pass


class SiteOfflineModels(SiteModels):

    """ Main controller of :class:`offline_models` objects.
    """

    module_name = "offline_models"
    register_historical = True

    @property
    def wrapper_cls(self):
        from .offline_model import OfflineModel

        return OfflineModel


site_offline_models = SiteOfflineModels()
