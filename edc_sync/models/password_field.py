from django import forms

from django_crypto_fields.fields import EncryptedCharField


class PasswordField(forms.CharField):
    widget = forms.PasswordInput


class PasswordModelField(EncryptedCharField):

    def formfield(self, **kwargs):
        defaults = {'form_class': PasswordField}
        defaults.update(kwargs)
        return super(PasswordModelField, self).formfield(**defaults)
