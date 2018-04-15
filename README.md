[![Build Status](https://travis-ci.org/clinicedc/edc-sync.svg?branch=develop)](https://travis-ci.org/clinicedc/edc-sync)
[![Coverage Status](https://coveralls.io/repos/clinicedc/edc-sync/badge.svg?branch=develop)](https://coveralls.io/r/clinicedc/edc-sync?branch=develop)

# edc-sync

Deploy a Django app as a client on laptop that is offline and sync the data with your server when you get back online.

### Installation

    pip install git+https://github.com/clinicedc/edc-sync@develop#egg=edc_sync

Add the pattern for access to the REST API:

    urlpatterns = [
        url(r'^edc-sync/', include('edc_sync.urls')),
    )

In settings.py:

    INSTALLED_APPS = [
    ...
    'edc_sync.apps.AppConfig',
    ...]

###Configure a model for synchronization

To include a model for synchronization declare the model with `BaseUuidModel` from `edc-base`, define the `natural_key` method and the model manager method `get_by_natural_key` and add the `HistoricalRecords` manager from `edc-base`.

For example the base class for all CRFs in a module might look like this:

    from edc_base.model.models import BaseUuidModel, HistoricalRecords
    
    from .visit import Visit

    class CrfModel(BaseUuidModel):
    
        visit = models.OneToOneField(Visit)
    
        objects = CrfModelManager()

        history = HistoricalRecords()
        
        def natural_key(self):
            return (self.visit.natural_key(), )
        natural_key.dependencies = ['myapp.visit']
    
        class Meta:
            abstract = True

### Add a model to the site global

In your app, add module `sync_models.py`.

    # sync_models.py
    
    from edc_sync.site_sync_models import site_sync_models
    from edc_sync.sync_model import SyncModel
    
    sync_models = [
        'my_app.CrfModel',
    ]
    
    site_sync_models.register(sync_models, SyncModel)
    
        
### Settings

to disable the `SyncModelMixin` add this to your settings.py

ALLOW_MODEL_SERIALIZATION = False  # (default: True)


### View models registered for synchronization

    from edc_sync.site_sync_models import site_sync_models
    
    # list all models in app 'bcpp_household' set for sync
    models = site_sync_models.site_models('bcpp_household', sync=True)
    
    # list all models in app 'bcpp_household' NOT set for sync
    models = site_sync_models.site_models('bcpp_household', sync=False)

    # list all models in app 'bcpp_household' not set for sync, excluding the "historical" models
    sync_models = [m.model._meta.label_lower for m in models if 'historical' not in m.model_name]

To create the model list for an apps `sync_models.py`, open a shell and list all models not yet registered for sync: 

    models = site_sync_models.site_models('bcpp_household', sync=False)
    [m.model._meta.label_lower for m in models if 'historical' not in m.model_name]

    
### About Synchronization

Synchronization is one-way and always toward a central server that has the master database for the project. Many clients push data to one server. 

#### Getting data from the field

We use __edc-sync__ in Django apps deployed to low-resourced remote communities where there is no reliable internet, public or private network. Our Research Assistants collect participant data in households, mobile tents and remote clinics. The Research Assistants enter data directly into their offline laptops. Once back online, data is pushed to the __community-server__ and later to the __central-server__. 

Our research also involves collecting blood specimens that need to get to our community clinic within an hour or two from time of collection. Research Assistants stay out in the field on shift for 6 hours or more. So we send a driver to fetch specimens and data from the Research Assistant in the field. The driver has a __middleman__ laptop that pulls all pending data from the Research Assistant's laptop. The driver and the Research Assistant then reconcile specimens and requisition data against the __middleman__ data and the physical specimen. (Note: we requisition and label specimens in the field through the app). The driver then returns to the community clinic, pushes data onto the __community-server__ and delivers all the specimens. The Lab Assistant then reconciles the specimens and requisition data against the __community-server__ data and the physical specimen.

#### Data Flow

__edc-sync__ uses either the REST API or FILE transfer:
- field client ---REST---> community server
- field client ---REST---> middleman (and modelre inspector) ---REST---> community server
- site server ---FILE---> central server

