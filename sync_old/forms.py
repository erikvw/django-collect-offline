from django import forms

from .models import Producer


class ProducerForm(forms.ModelForm):

    class Meta:
        model = Producer

    def clean(self):
        cleaned_data = self.cleaned_data
        return cleaned_data
