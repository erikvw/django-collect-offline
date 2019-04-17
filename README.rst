|pypi| |travis| |codecov| |downloads| |maintainability| |black|


django-collect-offline
----------------------

Deploy a Django app as a client on laptop that is offline and push the data to your server when you get back online.

Installation
------------

Add the pattern for access to the REST API:

.. code-block:: python

    urlpatterns = [
        url(r'^django-collect-offline/', include('django_collect_offline.urls')),
    )

In settings.py:

.. code-block:: python

    INSTALLED_APPS = [
    ...
    'django_collect_offline.apps.AppConfig',
    ...]

Configure a model for offline-use:
==================================

To include a model for offline-use declare the model with ``BaseUuidModel`` from ``edc-base``, define the ``natural_key`` method and the model manager method ``get_by_natural_key`` and add the ``HistoricalRecords`` manager from ``edc-base``.

For example the base class for all CRFs in a module might look like this:

.. code-block:: python

    from edc_model.models import BaseUuidModel, HistoricalRecords
    
    from .visit import Visit

    class CrfModel(BaseUuidModel):
    
        visit = models.OneToOneField(Visit)
    
        objects = CrfModelManager()

        history = HistoricalRecords()
        
        def natural_key(self):
            return (self.visit.natural_key(), )
        natural_key.dependencies = ['myapp.visit']
    
Add a model to the site global
==============================

In your app, add module ``offline_models.py``.

.. code-block:: python

    # offline_models.py
    
    from django_collect_offline.site_offline_models import site_offline_models
    from django_collect_offline.offline_model import OfflineModel
    
    offline_models = [
        'my_app.CrfModel',
    ]
    
    site_offline_models.register(offline_models, OfflineModel)
    
        
Settings
--------

to disable offline-use add this to your ``settings.py``

.. code-block:: python

    ALLOW_MODEL_SERIALIZATION = False  # (default: True)


View models registered for synchronization
==========================================

.. code-block:: python

    from django_collect_offline.site_offline_models import site_offline_models
    
    # list all models in app 'bcpp_household' set for offline-use
    models = site_offline_models.site_models('bcpp_household', sync=True)
    
    # list all models in app 'bcpp_household' NOT set for offline-use
    models = site_offline_models.site_models('bcpp_household', offline=False)

    # list all models in app 'bcpp_household' not set for offline-use, excluding the "historical" models
    offline_models = [m.model._meta.label_lower for m in models if 'historical' not in m.model_name]

To create the model list for an apps ``offline_models.py``, open a shell and list all models not yet registered for offline-use: 

.. code-block:: python

    models = site_offline_models.site_models('bcpp_household', offline=False)
    [m.model._meta.label_lower for m in models if 'historical' not in m.model_name]

    
About Offline-use
=================

The offline model approach is limited and only transfers data one-way and always toward a central server or parent node.
Many client nodes may push data to their server node. 

Getting data from the field
============================

We use ``django-collect-offline`` in Django projects deployed to low-resourced remote communities where there is no reliable internet, public or private network. Our Research Assistants collect participant data in households, mobile tents and remote clinics. The Research Assistants enter data directly into their offline laptops. Once back online, data is pushed to the ``community-server`` and later to the ``central-server``. 

Our research also involves collecting blood specimens that need to get to our community clinic within an hour or two from time of collection. Research Assistants stay out in the field on shift for 6 hours or more. So we send a driver to fetch specimens and data from the Research Assistant in the field. The driver has a ``middleman`` laptop that pulls all pending data from the Research Assistant's laptop. The driver and the Research Assistant then reconcile specimens and requisition data against the ``middleman`` data and the physical specimen. (Note: we requisition and label specimens in the field through the app). The driver then returns to the community clinic, pushes data onto the ``community-server`` and delivers all the specimens. The Lab Assistant then reconciles the specimens and requisition data against the ``community-server`` data and the physical specimen.

Data Flow
=========

``django-collect-offline`` uses either the REST API or FILE transfer:

* field client ---REST---> community server
* field client ---REST---> middleman (and modelre inspector) ---REST---> community server
* site server ---FILE---> central server


.. |pypi| image:: https://img.shields.io/pypi/v/django-collect-offline.svg
    :target: https://pypi.python.org/pypi/django-collect-offline
    
.. |travis| image:: https://travis-ci.org/erikvw/django-collect-offline.svg?branch=develop
    :target: https://travis-ci.org/erikvw/django-collect-offline
    
.. |codecov| image:: https://codecov.io/gh/erikvw/django-collect-offline/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/erikvw/django-collect-offline

.. |downloads| image:: https://pepy.tech/badge/django-collect-offline
   :target: https://pepy.tech/project/django-collect-offline

.. |maintainability| image:: https://api.codeclimate.com/v1/badges/e08f2bbee238af7bfdc7/maintainability
   :target: https://codeclimate.com/github/erikvw/django-collect-offline/maintainability
   :alt: Maintainability

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
   :alt: Code Style   

