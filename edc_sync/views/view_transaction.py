import json

from django.contrib.auth.decorators import login_required
from django.db.models import BinaryField
from django.apps import apps as django_apps
from django.shortcuts import render

from django_crypto_fields.classes import FieldCryptor


@login_required
def view_transaction(request, **kwargs):
    app_label = 'edc_sync'
    cryptor = FieldCryptor('aes', 'local')
    model_name = kwargs.get('model_name')
    pk = kwargs.get('pk')
    model = django_apps.get_model(app_label, model_name)
    obj = model.objects.get(pk=pk)
    for field in obj._meta.fields:
        if isinstance(field, BinaryField):
            decrypted_value = cryptor.decrypt(getattr(obj, field.name))
    obj = json.loads(decrypted_value)[0]
    return render(
        request, 'transaction.html', {'obj': obj, 'is_popup': True}, content_type="text/html")
