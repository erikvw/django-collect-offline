from django import forms

from .models import Producer


class ProducerForm(forms.ModelForm):

    class Meta:
        model = Producer


class UsbForm(forms.Form):

    path = forms.FilePathField(path='/')

    app_name = forms.CharField()
