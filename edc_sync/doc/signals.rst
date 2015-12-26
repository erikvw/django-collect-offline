Signals
=======

:mod:`bhp_sync` uses signals to:

* package a new or modified model instance into an outgoing transaction.
* extract and save a new or modified model instance from in an incoming transaction.

Signals are listening for:

* any model instance that is a base class of class :class:`BaseSyncModel` (:meth:`post_save`)
* any new instance of :class:`bhp_sync.models.IncomingTransaction` (:meth:`post_save`)

Models with the base class :class:`BaseSyncModel`
--------------------------------------------------
Outgoing transactions are created when models with the base class :class:`BaseSyncModel` are added or edited. When a model 
instance is saved the :meth:`post_save` signal calls :meth:`serialize_on_save`. For models that have a 
:class:`models.ManyToManyField`, the :meth:`serialize_m2m_on_save` is also called.

The methods called during the :meth:`post_save` signal, :meth:`serialize_on_save` and :meth:`serialize_m2m_on_save`,
are wrappers for :class:`bhp_sync.classes.SerializeToTransaction`.

:class:`bhp_sync.classes.SerializeToTransaction` packages the model instance as a transaction saved to :class:`bhp_sync.models.OutgoingTransaction`.

Transaction Models
------------------

:meth:`deserialize_on_post_save` is called by the :meth:`post_save` signal on 
instances of :class:`bhp_sync.models.IncomingTransaction`.

