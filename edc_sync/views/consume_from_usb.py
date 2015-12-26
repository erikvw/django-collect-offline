import platform

from os import listdir
from os.path import isfile, join, exists

from django.core.exceptions import ValidationError
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..classes import DeserializeFromTransaction
from ..models import Producer, IncomingTransaction


@login_required
def consume_from_usb(request, **kwargs):
    complete_json_list = []
    duplicates = 0
    app_name = kwargs.get('app_name')
    usb_path = kwargs.get('usb_path', get_usb_path(app_name))
    producers = Producer.objects.filter(is_active=True)
    for outgoing in get_complete_json_list(request, usb_path, app_name):
        if not IncomingTransaction.objects.filter(pk=outgoing['pk']).exists():
                IncomingTransaction.objects.create(
                    pk=outgoing['pk'],
                    tx_name=outgoing['fields']['tx_name'],
                    tx_pk=outgoing['fields']['tx_pk'],
                    tx=outgoing['fields']['tx'],
                    timestamp=outgoing['fields']['timestamp'],
                    producer=outgoing['fields']['producer'],
                    action=outgoing['fields']['action'])
        else:
            duplicates += 1
    messages.add_message(
        request, messages.INFO,
        'Successfully synchronized \'{0}\' transactions from the USB device \'{1}\', \'{2}\' '
        'where found to already be in the SERVER hence ignored'.format(
            len(complete_json_list), usb_path, duplicates))
    return render_to_response(
        'bcpp_sync.html', {'producers': producers}, context_instance=RequestContext(request))


def get_complete_json_list(request, usb_path, app_name, producers):
    complete_json_list = []
    deserializer = DeserializeFromTransaction()
    for file in get_file_pointers(usb_path, app_name):
        json_list = deserializer.deserialize_json_file(file)
        if not json_list:
            messages.add_message(
                request, messages.ERROR,
                'Synchronization from USB device of path \'{0}\' failed'.format(usb_path))
            return render_to_response(
                'sync.html', {'producers': producers, }, context_instance=RequestContext(request))
        complete_json_list.append(json_list)


def get_usb_path(app_name):
    if platform.system() == 'Darwin':
        usb_path = '/Volumes/{}_usb/'.format(app_name)
    else:
        usb_path = '/media/{}_usb/'.format(app_name)
    if not exists(usb_path):
        raise TypeError('Path does not exist. Got {}'.format(usb_path))
    return usb_path


def get_file_pointers(usb_path, app_name):
    file_pointers = []
    for f in listdir(usb_path):
        if isfile(join(usb_path, f)) and not (f.find(app_name) == -1):
            try:
                file_pointer = open(join(usb_path, f))
                file_pointers.append(file_pointer)
            except:
                raise ValidationError(
                    'Please insert a usb device named \'{0}_usb\', currently '
                    'using USB_PATH \'{1}\''.format(app_name, usb_path))
