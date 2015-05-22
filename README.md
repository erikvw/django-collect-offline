[![Build Status](https://travis-ci.org/botswana-harvard/edc-sync.svg?branch=develop)](https://travis-ci.org/botswana-harvard/edc-sync)
[![Coverage Status](https://coveralls.io/repos/botswana-harvard/edc-sync/badge.svg?branch=develop)](https://coveralls.io/r/botswana-harvard/edc-sync?branch=develop)
[![Code Health](https://landscape.io/github/botswana-harvard/edc-sync/develop/landscape.svg?style=flat)](https://landscape.io/github/botswana-harvard/edc-sync/develop)
[![PyPI version](https://badge.fury.io/py/edc-sync.svg)](http://badge.fury.io/py/edc-sync)

# edc-sync

Deploy a Django app as a client on laptop that is offline and sync the data with your server when you get back online.

Description
-----------
Synchronization is one-way and always toward a central server that has the master database for the project. Many clients push data to one server. 

We use __edc-sync__ in Django apps deployed to low-resourced remote communities where there is no reliable internet, public or private network. Our Research Assistants collect participant data in households, mobile tents and remote clinics. The Research Assistants enter data directly into their offline laptops. Once back online, data is pushed to the __community-server__ and later to the __central-server__. 

Our research often involves collecting blood specimens which need to get to our community clinic soon after collection. To allow the Research Assistants to remain in the field, we send a driver to the Research Assistant to fetch the specimens. The driver has a __middleman__ laptop that pulls all pending data from the Research Assistant's laptop. The driver and the Research Assistant then reconcile specimens and requisition data against the __middleman__ data and the physical specimen. (Note: we requisition and label specimens in the field through the app). The driver then returns to the community clinic, pushes data onto the __community-server__ and delivers all the specimens. The Lab Assistant then reconciles the specimens and requisition data against the __community-server__ data and the physical specimen.

__edc-sync__ uses either the REST API or FILE transfer:
- field client ---REST---> community server
- field client ---REST---> middleman (and model inspector) ---REST---> community server
- site server ---FILE---> central server

It is also possible to use Django's DB router if connections are good and reliable.



