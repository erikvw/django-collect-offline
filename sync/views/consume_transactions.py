import urllib2
import json

from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from edc.device.device.classes import Device
from edc.device.sync.classes import transaction_producer
from edc.device.sync.models import Producer, RequestLog, IncomingTransaction, MiddleManTransaction


class ConsumeTransactions(object):
    def __init__(self, request, producer, app_name):
        # If we have subclassed sync.html, then we need app_name to tell this view
        # To redirect to the application sync template instead of sync.html
        self.request = request
        self.app_name = app_name
        self._producer = None
        self.producer = producer
        self.device = Device()
        self.middleman = True if self.device.is_middleman else False
        try:
            api_key = request.user.api_key.key
        except AttributeError as attribute_error:
            if 'object has no attribute \'api_key\'' in str(attribute_error):
                raise ValueError('ApiKey does not exist for user {}. Check if tastypie '
                                 'was added to installed apps or Perhaps run '
                                 'create_api_key().'.format(self.request.user))
            elif 'object has no attribute \'key\'' in str(attribute_error):
                raise ValueError('ApiKey not found for user {}. Perhaps run '
                                 'create_api_key().'.format(self.request.user))
            raise
        except:
            raise ValueError('ApiKey not found for user {}. Perhaps run '
                             'create_api_key().'.format(self.request.user,))
        self.url_data = {'host': self.producer.url,
                         'producer': self.producer.name,
                         'limit': self.producer.json_limit,
                         'resource': 'outgoingtransaction',
                         'username': self.request.user.username,
                         'api_key': api_key}

    def __repr__(self):
        return 'ConsumeTransactions(<request>, {0.producer!r}, {0.app_name!r})'.format(self)

    def consume(self):
        # specify producer "name" of the server you are connecting to
        # as you only want transactions created by that server.
        if self.producer:
            # url to producer, add in the producer, username and api_key of the current user
            request_log = RequestLog()
            request_log.producer = self.producer
            request_log.save()
            self.producer.sync_datetime = request_log.request_datetime
            self.producer.sync_status = '?'
            self.producer.save()
            err = None
            try:
                req = urllib2.Request(url=self.url)
            except urllib2.URLError, err:
                req = None
                self.producer.sync_status = err
                self.producer.save()
                messages.add_message(self.request, messages.ERROR, '[A] {0} {1}'.format(err, self.url))
            while req:
                try:
                    f = urllib2.urlopen(req)
                    req = None
                except urllib2.HTTPError, err:
                    self.producer.sync_status = err
                    self.producer.save()
                    messages.add_message(self.request, messages.ERROR, '[B] {0} {1}'.format(err, self.url))
                    request_log.status = 'error'
                    request_log.save()
                    req = None
                    if err.code == 404:
                        messages.add_message(self.request, messages.ERROR,
                                             'Unknown producer. Got {}.'.format(self.producer))
                except urllib2.URLError, err:
                    self.producer.sync_status = err
                    self.producer.save()
                    request_log.status = 'error'
                    request_log.save()
                    messages.add_message(self.request, messages.ERROR, '[C] {0} {1}'.format(err, self.url))
                    break
                if not err:
                    # read response from url and decode
                    response = f.read()
                    json_response = None
                    if response:
                        json_response = json.loads(response)
                        # response is limited to 20 objects, if there are more
                        # next will the the url with offset to fetch next 20 (&limit=20&offset=20)
                        if 'meta' in json_response:
                            if json_response['meta']['next']:
                                req = urllib2.Request(url=json_response['meta']['next'])
                            if not json_response['meta']['total_count'] == 0:
                                messages.add_message(self.request, messages.INFO,
                                                     'Fetching. Limit is {}. Starting at {} of {}'.format(
                                                         json_response['meta']['limit'],
                                                         json_response['meta']['offset'],
                                                         json_response['meta']['total_count']))
                            self.producer.json_limit = json_response['meta']['limit']
                            self.producer.json_total_count = json_response['meta']['total_count']
                        if json_response:
                            messages.add_message(
                                self.request,
                                messages.INFO,
                                'Consuming {} new transactions from producer {}.'.format(
                                    len(json_response['objects']),
                                    self.producer.name))
                            # 'outgoing_transaction' is the serialized Transaction object from the producer.
                            # The OutgoingTransaction's object field 'tx' has the serialized
                            # instance of the data model we are looking for
                            for outgoing_transaction in json_response['objects']:
                                # save to IncomingTransaction.
                                # this will trigger the post_save signal to deserialize tx
                                # transanction_model = None
                                if self.middleman:
                                    # Read from Netbook's outgoing and create MiddleMan locally.
                                    # transanction_model = MiddleManTransaction
                                    try:
                                        middle_man_transaction = MiddleManTransaction.objects.get(pk=outgoing_transaction['id'])
                                        middle_man_transaction.is_consumed_server = False
                                        middle_man_transaction.is_error = False
                                        middle_man_transaction.save()
                                    except MiddleManTransaction.DoesNotExist:
                                        MiddleManTransaction.objects.create(
                                            pk=outgoing_transaction['id'],
                                            tx_name=outgoing_transaction['tx_name'],
                                            tx_pk=outgoing_transaction['tx_pk'],
                                            tx=outgoing_transaction['tx'],
                                            timestamp=outgoing_transaction['timestamp'],
                                            producer=outgoing_transaction['producer'],
                                            action=outgoing_transaction['action'])
                                else:
                                    # Then i must be a SERVER
                                    try:
                                        # START HERE
                                        # a little tricky cause it could be from Middleman or Netbook, depending on which was synced first
                                        # but either way, what we want to do is ignore the tranction that already exists in the server,
                                        # irregardles of where it comes from, it should exactly be the same transanction.
                                        incoming_transaction = IncomingTransaction.objects.get(pk=outgoing_transaction['id'])
                                        # incoming_transaction.is_consumed = False
                                        # incoming_transaction.is_error = False
                                        # incoming_transaction.save()
                                    except IncomingTransaction.DoesNotExist:
                                        IncomingTransaction.objects.create(
                                            pk=outgoing_transaction['id'],
                                            tx_name=outgoing_transaction['tx_name'],
                                            tx_pk=outgoing_transaction['tx_pk'],
                                            tx=outgoing_transaction['tx'],
                                            timestamp=outgoing_transaction['timestamp'],
                                            producer=outgoing_transaction['producer'],
                                            action=outgoing_transaction['action'])
                                # POST success back to to the producer
                                if self.middleman:
                                    outgoing_transaction['is_consumed_middleman'] = True
                                    outgoing_transaction['is_consumed_server'] = False
                                else:
                                    if not outgoing_transaction['is_consumed_middleman']:
                                        # transanction was consumed straight in the Server, MiddleMan bypassed
                                        outgoing_transaction['is_consumed_middleman'] = False
                                    outgoing_transaction['is_consumed_server'] = True
                                outgoing_transaction['consumer'] = transaction_producer
                                req = urllib2.Request(
                                    self.url,
                                    json.dumps(outgoing_transaction, cls=DjangoJSONEncoder),
                                    {'Content-Type': 'application/json'})
                                f = urllib2.urlopen(req)
                                response = f.read()
                                f.close()
                                self.producer.sync_status = 'OK'
                                self.producer.sync_datetime = datetime.today()
            self.producer.save()

    @property
    def producer(self):
        return self._producer

    @producer.setter
    def producer(self, producer):
        try:
            self._producer = Producer.objects.get(name__iexact=producer)
        except Producer.DoesNotExist:
            messages.add_message(self.request, messages.ERROR, 'Unknown producer. Got {}.'.format(producer))

    @property
    def remote_is_middleman(self):
        try:
            for middle_man_name in settings.MIDDLE_MAN_LIST:
                if self.producer.name == middle_man_name:
                    return True
        except AttributeError as attribute_error:
            if 'MIDDLE_MAN_LIST' in str(attribute_error):
                pass
        return False

    @property
    def remote_is_site_server(self):
        return self.device.is_producer_name_server(self.producer.name)

    @property
    def url(self):
        if self.middleman:
            # I am a Middleman and pulling from a netbook, so grab eligible(i.e not Synced
            # by Server and any MiddelMan yet) transactions from outgoingtransaction
            self.url_data.update(api_tx='api_otmr')
        else:
            if self.remote_is_middleman:
                # I am a Server pulling from a MiddleMan, we dont care who the original producer
                # was, just grab all eligible(i.e not synced by Server yet) tansanctions
                # in MiddleManTransaction table
                self.url_data.update(api_tx='api_mmtr')
                self.url_data.update(resource='middlemantransaction')
            elif self.remote_is_site_server:
                # I am a master server pulling from site servers, we pull from
                # OutgoingTransactions. We dont care who the original producer is, just grab them all.
                self.url_data.update(api_tx='api_otssr')
            else:
                # I am still a Server, but now pulling from a netbook, just grab all
                # eligible(i.e not synced by Server yet) transactions from OutgoingTransactions table
                # however pass the producer for filtering on the other side.
                self.url_data.update(api_tx='api_otsr')
        return ('{host}bhp_sync/{api_tx}/{resource}/?format=json&limit={limit}'
                '&username={username}&api_key={api_key}').format(**self.url_data)

    @property
    def redirect_url(self):
        if self.app_name:
            return reverse('bcpp_sync_url', args=(self.producer.name, ))
        else:
            return reverse('sync_consumed', args=(self.producer.name, ))


@login_required
def consume_transactions(request, **kwargs):
    consume_transactions = None
    if 'ALLOW_MODEL_SERIALIZATION' not in dir(settings):
        messages.add_message(request, messages.ERROR, 'ALLOW_MODEL_SERIALIZATION global boolean not found in settings.')
    try:
        consume_transactions = ConsumeTransactions(
            request,
            kwargs.get('producer', None),
            kwargs.get('app_name', settings.APP_NAME))
        consume_transactions.consume()
    except ValueError as value_error:
        if 'ApiKey not found' in str(value_error):
            messages.add_message(request, messages.ERROR, '{} {}'.format(str(value_error), 'Contact the Data Manager.'))
    except AttributeError as attribute_error:
        if 'ALLOW_MODEL_SERIALIZATION' in str(attribute_error):
            messages.add_message(request, messages.ERROR, (
                'Model serialization not enabled. To enable '
                'add \'ALLOW_MODEL_SERIALIZATION = True\' to settings. '
                'Contact the Data Manager'))
    if request.user and consume_transactions:
        return redirect(consume_transactions.redirect_url)
    return redirect(reverse('bcpp_sync_url'))
