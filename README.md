[![Build Status](https://travis-ci.org/botswana-harvard/edc-sync.svg?branch=develop)](https://travis-ci.org/botswana-harvard/edc-sync)
[![Coverage Status](https://coveralls.io/repos/botswana-harvard/edc-sync/badge.svg?branch=develop)](https://coveralls.io/r/botswana-harvard/edc-sync?branch=develop)
[![Code Health](https://landscape.io/github/botswana-harvard/edc-sync/develop/landscape.svg?style=flat)](https://landscape.io/github/botswana-harvard/edc-sync/develop)

# edc-sync

Deploy a Django app as a client on laptop that is offline and sync the data with your server when you get back online.

    pip install git+https://github.com/botswana-harvard/edc-sync@develop#egg=edc_sync

Add the pattern for access to the REST API:

    urlpatterns = [
        url(r'^edc-sync/', include('edc_sync.urls')),
    )

Try the `example` app in the repo. For example:

    $ mkvirtualenv -p /usr/local/bin/python3 --no-site-packages
    $ cd edc-sync/example
    $ pip install -r requirements.txt -U
    $ cd edc-sync
    $ python manage.py --settings='example.settings' migrate
    $ python manage.py --settings='example.settings' createsuperuser
    $ python manage.py --settings='example.settings' runserver


Description
===========

Synchronization
---------------
Synchronization is one-way and always toward a central server that has the master database for the project. Many clients push data to one server. 

Getting data from the field
---------------------------
We use __edc-sync__ in Django apps deployed to low-resourced remote communities where there is no reliable internet, public or private network. Our Research Assistants collect participant data in households, mobile tents and remote clinics. The Research Assistants enter data directly into their offline laptops. Once back online, data is pushed to the __community-server__ and later to the __central-server__. 

Our research also involves collecting blood specimens that need to get to our community clinic within an hour or two from time of collection. Research Assistants stay out in the field on shift for 6 hours or more. So we send a driver to fetch specimens and data from the Research Assistant in the field. The driver has a __middleman__ laptop that pulls all pending data from the Research Assistant's laptop. The driver and the Research Assistant then reconcile specimens and requisition data against the __middleman__ data and the physical specimen. (Note: we requisition and label specimens in the field through the app). The driver then returns to the community clinic, pushes data onto the __community-server__ and delivers all the specimens. The Lab Assistant then reconciles the specimens and requisition data against the __community-server__ data and the physical specimen.

### Data Flow

__edc-sync__ uses either the REST API or FILE transfer:
- field client ---REST---> community server
- field client ---REST---> middleman (and modelre inspector) ---REST---> community server
- site server ---FILE---> central server

It is also possible to use Django's DB router if connections are good and reliable (this option may be removed in future).


### Installation

In settings.py:

    INSTALLED_APPS = [
    ...
    'django_crypto_fields.apps.DjangoCryptoFieldsAppConfig',
    'edc_sync.apps.EdcSyncAppConfig',
    ...]

### Encryption and `edc_sync`
To use `edc_sync` and `django_crypto_fields` together requires additional configuration.

#### Model `Crypt`
Although transactions are serialized to JSON, encrypted, and stored in models such as `IncomingTransaction` and `OutgoingTransaction`, the JSON objects use AES encryption and do not update the reference model in `django_crypto_fields`, `django_crypto_fields.models.crypt`. However, it is very likely that your app has models that use encrypted fields and do update the `Crypt` model. If so, the `Crypt` model must also be synchronized so that the receiving database can decrypt. To enable this, you need to declare the model in your app with the `SyncModelMixin` and used the `BaseUuidModel` to change the `primary_key` from an `IntegerField` to a `UUIDField`. 
For example: 
    
    from django_crypto_fields.crypt_model_mixin import CryptModelMixin
    from edc_base.model.models import BaseUuidModel
    from edc_sync.models import SyncModelMixin

    class Crypt(CryptModelMixin, SyncModelMixin, BaseUuidModel):

        class Meta:
            app_label = 'example'
            unique_together = (('hash', 'algorithm', 'mode'),)

then in your `example.apps.py`: 

    from django_crypto_fields.apps import DjangoCryptoFieldsAppConfig

    class DjangoCryptoFieldsApp(DjangoCryptoFieldsAppConfig):
        name = 'django_crypto_fields'
        model = ('example', 'crypt')

then in settings:

    INSTALLED_APPS = [
    ...
    'edc_sync.apps.DjangoCryptoFieldsApp',
    'edc_sync.apps.EdcSyncAppConfig',
    ...]
        
#### DATABASES attribute in `settings`
Using `edc_sync` suggests a multi-database environment. In the rare case that the default database named in your `settings.DATABASES` is not named `default`, you need to tell `django_crypto_fields` to get the `using` value from the app config attribute `crypto_model_using`. This attribute only affects access to the `Crypt` model.

For example, in your `example.apps.py`: 

    from django_crypto_fields.apps import DjangoCryptoFieldsAppConfig

    class DjangoCryptoFieldsApp(DjangoCryptoFieldsAppConfig):
        name = 'django_crypto_fields'
        model = ('example', 'crypt')
        crypt_model_using = 'client'

### Audit trail manager on models
Edc apps use `django_simple_history` to keep a full audit trail of data modifications. For an audit trail to synchronize with `edc_sync`, use class `edc_sync.models.SyncHistoricalRecords` in place of `simple_history.model.HistoricalRecords`. See section below on configuring a model. 

###Configure a model for synchronization

To include a model add the `SyncModelMixin`. For example the base class for all CRFs in a module might look like this:

    from edc_base.model.models import BaseUuidModel
    from edc_consent.models RequiresConsentMixin
    from edc_offstudy.models import OffStudyMixin
    from edc_sync.models import SyncModelMixin, SyncHistoricalRecords
    from edc_visit_tracking.models import CrfModelMixin
    
    from .maternal_consent import MaternalConsent

    class MaternalCrfModel(CrfModelMixin, SyncModelMixin, OffStudyMixin,
                           RequiresConsentMixin, BaseUuidModel):
    
        consent_model = MaternalConsent
    
        off_study_model = ('mb_maternal', 'MaternalOffStudy')
    
        maternal_visit = models.OneToOneField(MaternalVisit)
    
        history = SyncHistoricalRecords()
    
        entry_meta_data_manager = CrfMetaDataManager(MaternalVisit)
    
        def natural_key(self):
            return (self.maternal_visit.natural_key(), )
        natural_key.dependencies = ['mb_maternal.maternal_visit']
    
        def __str__(self):
            return str(self.get_visit())
    
        class Meta:
            abstract = True

        
`SyncModelMixin` needs model method `natural_key` and the model manager method `get_by_natural_key`. If either or both do not exist, a `SyncError` Exception is raises. In the example above, the `CrfModelMixin` declares the `objects` model manager that includes the required manager method.

For any insert, update or delete of concrete models based on `MaternalCrfModel`, the `SyncModelMixin` creates `OutgoingTransaction` instances on the same DB as the concrete model.

### Copy transactions from one DB to another

Data entered on 'client' eventually needs to be synchronized to 'server'. Your `settings.DATABASES` might be like this:
    
    DATABASES = {
        'default': {},
        'server': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        },
        'client': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
      
As data is entered on `client`, the data is serialized into model `OutgoingTransaction` on `client`. The outgoing transactions on `client` are can be copied to `server` like this:

    OutgoingTransaction.objects.using('client').filter(
            is_consumed_server=False).copy_to_incoming_transaction('server') 

Once the transactions are on `server` they are deserialized like this:

    messages = IncomingTransaction.objects.using('server').filter(
        is_consumed=False).deserialize(custom_device=device, check_hostname=False)

### Settings

to disable the `SyncModelMixin` add this to your settings.py

ALLOW_MODEL_SERIALIZATION = False  # (default: True)

### EDC Sync File Transfer

With a stable connectivity between client and server then we use the REST API to sync transactions with the server. 
Alternatively our remote data systems can generate transaction files in the field with a client machine, 
then the files need to be transfered to the community server. Non technical users(RA's) must transfer the generated files
to the community server using edc sync file transfer. Edc sync file transfer use paramiko to connect to the community server and transfer newly generated files.


### Data Flow

- field client ---Paramiko---> community server

### Required Attributes in Settings.py

Add the following to settings.py

* LOCAL_TRANSACTION_DIR= /path/to/local transactions/

* LOCAL_ARCHIVE_DIR = /path/to/archive/files/

* LOCAL_MEDIA_DIR = /path/to/media files/

* REMOTE_SERVER_IP = IP Address

* REMOTE_MEDIA_DIR = /path/to/transfer/media files/to/

* REMOTE_TRANSACTION_DIR = /path/to/transfer files/to/

## TODO

* handle proxy models
* producer
* handle deleted transactions
