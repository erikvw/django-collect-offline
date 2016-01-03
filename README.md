[![Build Status](https://travis-ci.org/botswana-harvard/edc-sync.svg?branch=develop)](https://travis-ci.org/botswana-harvard/edc-sync)
[![Coverage Status](https://coveralls.io/repos/botswana-harvard/edc-sync/badge.svg?branch=develop)](https://coveralls.io/r/botswana-harvard/edc-sync?branch=develop)
[![Code Health](https://landscape.io/github/botswana-harvard/edc-sync/develop/landscape.svg?style=flat)](https://landscape.io/github/botswana-harvard/edc-sync/develop)

# edc-sync

Deploy a Django app as a client on laptop that is offline and sync the data with your server when you get back online.


urlpatterns += patterns(
    '',
    (r'^bhp_sync/', include('edc_sync.urls')),
)


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
- field client ---REST---> middleman (and model inspector) ---REST---> community server
- site server ---FILE---> central server

It is also possible to use Django's DB router if connections are good and reliable.


###Configure a model for synchronization

To include a model add the `SyncModelMixin`. For example the base class for all CRFs in a module might look like this:

    from edc_base.model.models import BaseUuidModel
    from edc_consent.models RequiresConsentMixin
    from edc_offstudy.models import OffStudyMixin
    from edc_sync.models import SyncModelMixin
    from edc_visit_tracking.models import CrfModelMixin
    
    from .maternal_consent import MaternalConsent

    class MaternalCrfModel(CrfModelMixin, SyncModelMixin, OffStudyMixin,
                           RequiresConsentMixin, BaseUuidModel):
    
        consent_model = MaternalConsent
    
        off_study_model = ('mb_maternal', 'MaternalOffStudy')
    
        maternal_visit = models.OneToOneField(MaternalVisit)
    
        history = AuditTrail()
    
        entry_meta_data_manager = CrfMetaDataManager(MaternalVisit)
    
        def natural_key(self):
            return (self.maternal_visit.natural_key(), )
        natural_key.dependencies = ['mb_maternal.maternal_visit']
    
        def __unicode__(self):
            return unicode(self.get_visit())
    
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

