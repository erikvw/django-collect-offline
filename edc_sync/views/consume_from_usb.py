import json
import platform

from os import listdir
from os.path import isfile, join, exists

from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from ..models import Producer, IncomingTransaction
from ..forms import UsbForm


class ConsumeFromUsbView(FormView):

    form_class = UsbForm
    initial = {'key': 'value'}
    template_name = 'form_template.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ConsumeFromUsbView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        producers = Producer.objects.filter(is_active=True)
        return render(request, self.template_name, {
            'form': form,
            'producers': producers})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            self.consume_from_usb(form.cleaned_data)
            return HttpResponseRedirect('/success/')
        return render(request, self.template_name, {'form': form})

    def consume_from_usb(self, request, **kwargs):
        skipped = 0
        created = 0
        app_name = kwargs.get('app_name')
        usb_path = kwargs.get('usb_path', self.get_usb_path(app_name))
        for outgoing_transaction in self.get_outgoing_transactions_as_json(request, usb_path, app_name):
            options = dict(
                pk=outgoing_transaction['pk'],
                tx_name=outgoing_transaction['fields']['tx_name'],
                tx_pk=outgoing_transaction['fields']['tx_pk'],
                tx=outgoing_transaction['fields']['tx'],
                timestamp=outgoing_transaction['fields']['timestamp'],
                producer=outgoing_transaction['fields']['producer'],
                action=outgoing_transaction['fields']['action'])
            try:
                IncomingTransaction.objects.get(**options)
                skipped += 1
            except IncomingTransaction.DoesNotExist:
                IncomingTransaction.objects.create(**options)
                created += 1
        messages.add_message(
            self.request, messages.INFO,
            'Successfully synchronized \'{0}\' transactions from the USB device \'{1}\', \'{2}\' '
            'transactions where found to already exist on the SERVER and were ignored'.format(
                created, usb_path, skipped))

    def deserialize_json_file(self, path):
        with open(path, 'r') as f:
            json_txt = f.read()
            decoded = json.loads(json_txt)
        return decoded

    def get_outgoing_transactions_as_json(self, request, usb_path, app_name, producers):
        """Returns a list of """
        complete_json_list = []
        for filename in listdir(usb_path):
            if isfile(join(usb_path, filename)) and not (filename.find(app_name) == -1):
                json_list = self.deserialize_json_file(join(usb_path, filename))
                if not json_list:
                    messages.add_message(
                        request, messages.ERROR,
                        'Synchronization from USB device of path \'{0}\' failed'.format(usb_path))
                    return render_to_response(
                        'sync.html', {'producers': producers, }, context_instance=RequestContext(request))
        return complete_json_list.append(json_list)

    def get_usb_path(self, app_name):
        if platform.system() == 'Darwin':
            usb_path = '/Volumes/{}_usb/'.format(app_name)
        else:
            usb_path = '/media/{}_usb/'.format(app_name)
        if not exists(usb_path):
            raise TypeError('Path does not exist. Got {}'.format(usb_path))
        return usb_path
