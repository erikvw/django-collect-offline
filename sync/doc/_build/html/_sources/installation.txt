Installation
============

Checkout the latest version of :mod:`bhp_sync` into your project folder::

    svn co http://192.168.1.50/svn/bhp_sync

Checkout two additional modules::

    svn co http://192.168.1.50/svn/bhp_base_model
    svn co http://192.168.1.50/svn/bhp_common


Add :mod:`bhp_sync` to your project ''settings'' file::

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.admin',
        'django.contrib.admindocs',
        'django_extensions',
        'audit_trail',
        'bhp_base_model',
        'bhp_common',
        'bhp_sync',
        ...
        )
      
Install Tastypie::

    sudo easy_install tastypie        
        
