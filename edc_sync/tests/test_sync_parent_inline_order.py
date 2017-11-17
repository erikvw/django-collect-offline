from django.test import TestCase, tag

from django.contrib import admin
from django import forms

from django.forms import inlineformset_factory
from edc_base.modeladmin_mixins import TabularInlineMixin
from edc_device.constants import NODE_SERVER
from django.contrib.admin.sites import AdminSite
from edc_sync.transaction.transaction_deserializer import TransactionDeserializer
from edc_sync_files.transaction import TransactionExporter, TransactionImporter


# from ..models import OutgoingTransaction
from .models import TestModel, TestModelWithFkProtected
from ..site_sync_models import site_sync_models
from ..sync_model import SyncModel


class MockRequest:
    pass


class MockSuperUser:

    def has_perm(self, perm):
        return True


request = MockRequest()
# request.POST = {'csrfmiddlewaretoken': ['QJSUrTFPNboyaqd15kyWQetgKMEYQSDDrzrNHpYEQfuyqH0Cu4Yl5RaoYzpntfK6'],
#                 'f1': ['www'], 'f2': ['eeee'], 'f3': ['eb26e38e'],
#                 'testmodelwithfkprotected_set-TOTAL_FORMS': ['1'],
#                 'testmodelwithfkprotected_set-INITIAL_FORMS': ['0'],
#                 'testmodelwithfkprotected_set-MIN_NUM_FORMS': ['0'],
#                 'testmodelwithfkprotected_set-MAX_NUM_FORMS': ['1000'],
#                 'testmodelwithfkprotected_set-0-id': [''],
#                 'testmodelwithfkprotected_set-0-test_model': [''],
#                 'testmodelwithfkprotected_set-0-device_created': [''],
#                 'testmodelwithfkprotected_set-0-device_modified': [''],
#                 'testmodelwithfkprotected_set-0-f1': ['ccccccc'],
#                 'testmodelwithfkprotected_set-__prefix__-id': [''],
#                 'testmodelwithfkprotected_set-__prefix__-test_model': [''],
#                 'testmodelwithfkprotected_set-__prefix__-device_created': [''],
#                 'testmodelwithfkprotected_set-__prefix__-device_modified': [''],
#                 'testmodelwithfkprotected_set-__prefix__-f1': [''],
#                 '_save': ['Save']}
request.user = MockSuperUser()


class TestModelForm(forms.ModelForm):

    class Meta:
        model = TestModel
        fields = '__all__'


class TestModelWithFkProtectedForm(forms.ModelForm):

    class Meta:
        model = TestModelWithFkProtected
        fields = '__all__'


class TestModelWithFkProtectedInline(TabularInlineMixin, admin.TabularInline):

    model = TestModelWithFkProtected
    form = TestModelWithFkProtectedForm
    extra = 3


class TestModelAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['f1', 'f2', 'f3']}),
    ]
    inlines = [TestModelWithFkProtectedInline]

# admin.site.register(TestModel, TestModelAdmin)


@tag('parent_inline')
class TestParentInlineSync(TestCase):

    def setUp(self):
        site_sync_models.registry = {}
        site_sync_models.loaded = False
        self.site = AdminSite()

        sync_models = [
            'edc_sync.testmodel', 'edc_sync.testmodelwithfkprotected']
        site_sync_models.register(sync_models, sync_model_cls=SyncModel)
        self.data = {'csrfmiddlewaretoken': ['Wnr6TsxEOkBqKhq0lBKn5Vi9zz6aGZunxd0Z9YQtRoHq0ydBKlaMkyZhNmRzjmBQ'], 'f1': ['test 1'], 'f2': ['test 2'], 'f3': ['156a3c30'], 'testmodelwithfkprotected_set-TOTAL_FORMS': ['1'], 'testmodelwithfkprotected_set-INITIAL_FORMS': ['0'], 'testmodelwithfkprotected_set-MIN_NUM_FORMS': ['0'], 'testmodelwithfkprotected_set-MAX_NUM_FORMS': ['1000'], 'testmodelwithfkprotected_set-0-id': [''], 'testmodelwithfkprotected_set-0-test_model': [
            ''], 'testmodelwithfkprotected_set-0-device_created': [''], 'testmodelwithfkprotected_set-0-device_modified': [''], 'testmodelwithfkprotected_set-0-f1': ['inline 10'], 'testmodelwithfkprotected_set-__prefix__-id': [''], 'testmodelwithfkprotected_set-__prefix__-test_model': [''], 'testmodelwithfkprotected_set-__prefix__-device_created': [''], 'testmodelwithfkprotected_set-__prefix__-device_modified': [''], 'testmodelwithfkprotected_set-__prefix__-f1': [''], '_save': ['Save']}

    def test_form_data0(self):
        tm = TestModelAdmin(TestModel, self.site)
        print(request.user.__dict__)

#     def test_form_data(self):
#         form = TestModelForm(data=self.data)
#         form.save()
#         self.assertEqual(TestModel.objects.all().count(), 1)
#         self.assertEqual(TestModelWithFkProtected.objects.all().count(), 1)


#     def test_create_parent_inline_transactions(self):
#         test_model_form = TestModelForm(
#             f1='test1', f2='test2', f3='test3')
#         test_model_with_fk_protected_form = TestModelWithFkProtectedForm(
#             instance=test_model_form)
#
#         test_model = TestModel.objects.using('client').create(f1='model1')
#         TestModelWithFkProtected.objects.using(
#             'client').create(f1='f1', test_model=test_model)
# #         for tx in OutgoingTransaction.objects.using('client').all():
# #             print(tx.timestamp, tx.tx_name, tx.producer)
