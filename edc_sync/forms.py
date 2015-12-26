from django import forms

from .models import Producer


class ProducerForm(forms.ModelForm):

    class Meta:
        model = Producer
