Overview
========

:mod:`bhp_sync` is used to synchronize data modifications of identical models between EDC implementations. A typical scenario
would be between a group of netbooks and a central server where each netbook and the server are running the same 
EDC system.

Each model instance saved on the netbook is serialized and packed as an outgoing transaction. 
The outgoing transaction is transferred to, unpacked and deserialized by the server as an incoming transaction.

The packing of outgoing transactions and unpacking of incoming transactions is handled with signals while the communication
between systems is done with a REST API (Tastypie).

