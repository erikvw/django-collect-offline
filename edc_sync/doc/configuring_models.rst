Configuring models to use bhp_sync
==================================

Change the base class of the model to :class:`bhp_sync.classes.base_sync_model`.

For example, given a model of laboratory test panels, enable synchronization by adding::
    
    from edc.device.sync.classes import BaseSyncModel as BaseModel
    
    class Panel(BaseModel):
    
        ...

or it might be better to make the import conditional like this::

    try:
        from edc.device.sync.classes import BaseSyncModel as BaseModel
    except ImportError:
        from edc_base.model.classes import BaseModel
        
    class Panel(BaseModel):
    
        ...
        
and finally:

.. code-block:: python
    :emphasize-lines: 3  
    
    from django.db import models
    try:
        from edc.device.sync.classes import BaseSyncModel as BaseModel
    except ImportError:
        from edc_base.model.classes import BaseModel
    from lab_aliquot_list import AliquotType
    from panel_group import PanelGroup
    
    
    class Panel(BaseModel):    
        
        name = models.CharField(
            verbose_name = "Panel Name", 
            max_length = 50,  
            unique = True,
            db_index = True,                
            )
        
        panel_group = models.ForeignKey(PanelGroup)
        
        test_code = models.ManyToManyField(TestCode,
            verbose_name = 'Test Codes',
            help_text = 'Choose all that apply',
            )
                    
        aliquot_type = models.ManyToManyField(AliquotType,
            help_text = 'Choose all that apply',
            )
                    
        comment = models.CharField(
            verbose_name = "Comment", 
            max_length = 250, 
            blank = True,
            )   
            
        def __unicode__(self):
            return self.name
            
        class Meta:
            app_label = 'lab_panel'        
