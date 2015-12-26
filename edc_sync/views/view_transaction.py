from django.contrib.auth.decorators import login_required
from django.db.models import TextField
from django.db.models import get_model
from django.shortcuts import render_to_response
from django.template import RequestContext

from edc_base.encrypted_fields import EncryptedTextField, FieldCryptor


@login_required
def view_transaction(request, **kwargs):
    cryptor = FieldCryptor('aes', 'local')
    app_label = kwargs.get('app_label', 'sync')
    model_name = kwargs.get('model_name')
    pk = kwargs.get('pk')
    model = get_model(app_label, model_name)
    model_instance = model.objects.get(pk=pk)
    textfields = {}
    charfields = {}
    for field in model_instance._meta.fields:
        if isinstance(field, (TextField, EncryptedTextField)):
            value = getattr(model_instance, field.name)
            if (cryptor.is_encrypted(value)):
                cipher = cryptor.decrypt(value)
                textfields.update({field.name: cipher})
            else:
                textfields.update({field.name: value})
        else:
            charfields.update({field.name: getattr(model_instance, field.name)})
    return render_to_response('transaction.html', {
        'charfields': charfields, 'textfields': textfields},
        context_instance=RequestContext(request))
