from django.contrib import admin

from .models import TestModel, Crypt, ComplexTestModel, M2m, Fk


from django_crypto_fields.admin import CryptModelAdmin
from django.contrib.admin.sites import AdminSite


class ExampleAdminSite(AdminSite):
    site_header = 'Example Administration'
    site_title = 'Example Administration'
    index_title = 'Example Administration'
    site_url = '/example/'

example_admin = ExampleAdminSite(name='example_admin')


@admin.register(Crypt, site=example_admin)
class CryptModelAdmin(CryptModelAdmin):
    pass


@admin.register(TestModel, site=example_admin)
class TestModelAdmin(admin.ModelAdmin):
    pass


@admin.register(ComplexTestModel, site=example_admin)
class ComplexTestModelAdmin(admin.ModelAdmin):
    pass


@admin.register(M2m, site=example_admin)
class M2mAdmin(admin.ModelAdmin):
    pass


@admin.register(Fk, site=example_admin)
class FkAdmin(admin.ModelAdmin):
    pass
