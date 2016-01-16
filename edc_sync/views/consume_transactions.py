import json
import requests

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils import timezone

from edc_device import Device
from edc_sync.api.resource import OutgoingTransactionResource

from ..exceptions import SyncError
from ..models import Producer, RequestLog, transaction_producer


class ConsumeTransactions(object):

    def __init__(self, request, producer_name=None, host=None, url=None, app_name=None):
        self.app_name = None  # app_name or settings.APP_NAME
        self.device = Device()
        if not self.device.is_server:
            raise SyncError(
                'Only servers may fetch transactions from another device. Got {}'.format(str(self.device)))
        self.producer = self.get_producer(producer_name)
        self.request = request
        self.params = {'host': self.producer.url or 'http://localhost:8000/',
                       'producer': self.producer.name,
                       'limit': self.producer.json_limit,
                       'resource': 'outgoingtransaction',
                       'username': self.request.user.username,
                       'api_key': self.api_key}
        self.url = ('{host}edc_sync/api/v1/{resource}/?format=json&limit={limit}'
                    '&username={username}&api_key={api_key}').format(**self.params)

    def __repr__(self):
        return 'ConsumeTransactions(<request>, {0.producer!r}, {0.app_name!r})'.format(self)

    def update_log(self):
        request_log = RequestLog()
        request_log.producer = self.producer
        request_log.save()
        self.producer.sync_datetime = request_log.request_datetime
        self.producer.sync_status = '?'
        self.producer.save()

    def consume(self):
        response = requests.get(self.url)
        print(response)
        json_response = json.loads(r.data)
        return None
#             # response is limited to 20 objects, if there are more
#             # next will the the url with offset to fetch next 20 (&limit=20&offset=20)
#             if 'meta' in json_response:
#                 if json_response['meta']['next']:
#                     req = urllib2.Request(url=json_response['meta']['next'])
#                 if not json_response['meta']['total_count'] == 0:
#                     messages.add_message(self.request, messages.INFO,
#                                          'Fetching. Limit is {}. Starting at {} of {}'.format(
#                                              json_response['meta']['limit'],
#                                              json_response['meta']['offset'],
#                                              json_response['meta']['total_count']))
#                 self.producer.json_limit = json_response['meta']['limit']
#                 self.producer.json_total_count = json_response['meta']['total_count']
#             if json_response:
#                 messages.add_message(
#                     self.request,
#                     messages.INFO,
#                     'Consuming {} new transactions from producer {}.'.format(
#                         len(json_response['objects']),
#                         self.producer.name))
#                 for outgoing_transaction in json_response['objects']:
#                     outgoing_transaction.to_incoming_transaction()
#                     if self.device.is_middleman:
#                         outgoing_transaction['is_consumed_middleman'] = True
#                     else:
#                         outgoing_transaction['is_consumed_server'] = True
#                     outgoing_transaction['consumer'] = transaction_producer
#                     req = urllib2.Request(
#                         self.url,
#                         json.dumps(outgoing_transaction, cls=DjangoJSONEncoder),
#                         {'Content-Type': 'application/json'})
#                     f = urllib2.urlopen(req)
#                     response = f.read()
#                     f.close()
#                     self.producer.sync_status = 'OK'
#                     self.producer.sync_datetime = timezone.now()
#             self.producer.save()

    @property
    def api_key(self):
        try:
            api_key = self.request.user.api_key.key
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
        return api_key

    def get_producer(self, producer_name):
        try:
            producer = Producer.objects.get(name__iexact=producer_name)
        except Producer.DoesNotExist:
            producer = None
            messages.add_message(self.request, messages.ERROR,
                                 'Unknown producer. Got \'{}\'.'.format(producer_name))
        return producer

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
        hostname = self.producer.name.split('-')[0]
        if hostname.find('bcpp') != -1 and int(hostname[4:]) in self.device.server_ids:
            return True
        return False

#     @property
#     def url(self):
#         if self.device.is_middleman:
#             # I am a Middleman and pulling from a netbook, so grab eligible(i.e not Synced
#             # by Server and any MiddelMan yet) transactions from outgoingtransaction
#             self.url_data.update(api_tx='api_otmr')
#         else:
#             if self.remote_is_middleman:
#                 # I am a Server pulling from a MiddleMan, we dont care who the original producer
#                 # was, just grab all eligible(i.e not synced by Server yet) tansanctions
#                 # in MiddleManTransaction table
#                 self.url_data.update(api_tx='api_mmtr')
#                 self.url_data.update(resource='middlemantransaction')
#             elif self.remote_is_site_server:
#                 # I am a master server pulling from site servers, we pull from
#                 # OutgoingTransactions. We dont care who the original producer is, just grab them all.
#                 self.url_data.update(api_tx='api_otssr')
#             else:
#                 # I am still a Server, but now pulling from a netbook, just grab all
#                 # eligible(i.e not synced by Server yet) transactions from OutgoingTransactions table
#                 # however pass the producer for filtering on the other side.
#                 self.url_data.update(api_tx='api_otsr')
#         return ('{host}edc_sync/{api_tx}/{resource}/?format=json&limit={limit}'
#                 '&username={username}&api_key={api_key}').format(**self.url_data)

    @property
    def redirect_url(self):
        if self.app_name:
            return reverse('bcpp_sync_url', args=(self.producer.name, ))
        else:
            return reverse('sync_consumed', args=(self.producer.name, ))

    def get_request(self):
        try:
            request = urllib2.Request(url=self.url)
        except urllib2.URLError as err:
            request = None
            self.producer.sync_status = err
            self.producer.save()
            messages.add_message(self.request, messages.ERROR, '[A] {0} {1}'.format(err, self.url))
        return request

    def get_url_data(self, request):
        try:
            url_data = urllib2.urlopen(request)
        except urllib2.HTTPError as err:
            self.producer.sync_status = err
            self.producer.save()
            messages.add_message(self.request, messages.ERROR, '[B] {0} {1}'.format(err, self.url))
            if err.code == 404:
                messages.add_message(self.request, messages.ERROR,
                                     'Unknown producer. Got {}.'.format(self.producer))
        except urllib2.URLError as err:
            self.producer.sync_status = err
            self.producer.save()
            messages.add_message(self.request, messages.ERROR, '[C] {0} {1}'.format(err, self.url))
        return url_data


@login_required
def consume_transactions(request, **kwargs):
    consume_transactions = None
    try:
        consume_transactions = ConsumeTransactions(
            request,
            kwargs.get('producer', None),
            kwargs.get('app_name', settings.APP_NAME))
        consume_transactions.consume()
    except ValueError as e:
        if 'ApiKey not found' in str(e):
            messages.add_message(
                request, messages.ERROR, '{} {}'.format(str(e), 'Contact the Data Manager.'))
        else:
            raise ValueError(e)
    if request.user and consume_transactions:
        return redirect(consume_transactions.redirect_url)
    return redirect(reverse('bcpp_sync_url'))
