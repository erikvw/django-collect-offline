from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key
for user in User.objects.all():
    if not ApiKey.objects.filter(user=user):
        create_api_key(instance=user, created=True)

from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key
for user in User.objects.filter(username__in=names):
    if not ApiKey.objects.filter(user=user):
        ApiKey.objects.create(user=user)

api_key = ApiKey.objects.get(user=User.objects.get(username='erikvw'))
api_key.key='1af87bd7d0c7763e7b11590c9398740f0de7678b'
api_key.save()

api_key = ApiKey.objects.get(user=User.objects.get(username='kbinda'))
api_key.key='0a0b09212e2661d01b09ffe2c780145dc86c1cd6'
api_key.save()

api_key = ApiKey.objects.get(user=User.objects.get(username='tlentswe'))
api_key.key='93d15e5d8b8c589c28be956a4419d18c5c657924'
api_key.save()

api_key = ApiKey.objects.get(user=User.objects.get(username='django'))
api_key.key='1af87bd7d0c7763e7b11590c9398740f0de7678b'
api_key.save()
names = ['onep','ckgathi','chick','django','erikvw','jtshikedi','rmabutho','ankhutelang', 'tbasuti', 'tmoruiemang', 'ambikiwa', 'ksebinang', 'kkeothepile', 'lmmesi', 'lramatokwane', 'nkeakantse', 'smbayi', 'tkgautlhe']

if you get <<ValueError: astimezone() cannot be applied to a naive datetime>> when trying to create ApiKeys,
replace
def now:
    return timezone.localtime.(timezone.now())
with
def now():
        d = timezone.now()
        if d.tzinfo:
           return timezone.localtime(timezone.now())
        return d
at python2.7/site-packages/tastypie/utils/timezone.py.
