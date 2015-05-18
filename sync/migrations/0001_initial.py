# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'IncomingTransaction'
        db.create_table('bhp_sync_incomingtransaction', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('user_created', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('user_modified', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('hostname_created', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('hostname_modified', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('revision', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('tx', self.gf('django.db.models.fields.TextField')()),
            ('tx_name', self.gf('django.db.models.fields.CharField')(max_length=64, db_index=True)),
            ('tx_pk', self.gf('django.db.models.fields.CharField')(max_length=36, db_index=True)),
            ('producer', self.gf('django.db.models.fields.CharField')(default='mac-bhp066', max_length=50, db_index=True)),
            ('action', self.gf('django.db.models.fields.CharField')(default='I', max_length=1)),
            ('timestamp', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, db_index=True)),
            ('consumed_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('consumer', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=25, null=True, blank=True)),
            ('is_ignored', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('is_error', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('error', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True, blank=True)),
            ('batch_seq', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('batch_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('is_consumed', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('is_self', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal('sync', ['IncomingTransaction'])

        # Adding model 'OutgoingTransaction'
        db.create_table('bhp_sync_outgoingtransaction', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('user_created', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('user_modified', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('hostname_created', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('hostname_modified', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('revision', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('tx', self.gf('django.db.models.fields.TextField')()),
            ('tx_name', self.gf('django.db.models.fields.CharField')(max_length=64, db_index=True)),
            ('tx_pk', self.gf('django.db.models.fields.CharField')(max_length=36, db_index=True)),
            ('producer', self.gf('django.db.models.fields.CharField')(default='mac-bhp066', max_length=50, db_index=True)),
            ('action', self.gf('django.db.models.fields.CharField')(default='I', max_length=1)),
            ('timestamp', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, db_index=True)),
            ('consumed_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('consumer', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=25, null=True, blank=True)),
            ('is_ignored', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('is_error', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('error', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True, blank=True)),
            ('batch_seq', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('batch_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('is_consumed_middleman', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('is_consumed_server', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal('sync', ['OutgoingTransaction'])

        # Adding model 'MiddleManTransaction'
        db.create_table('bhp_sync_middlemantransaction', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('user_created', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('user_modified', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('hostname_created', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('hostname_modified', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('revision', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('tx', self.gf('django.db.models.fields.TextField')()),
            ('tx_name', self.gf('django.db.models.fields.CharField')(max_length=64, db_index=True)),
            ('tx_pk', self.gf('django.db.models.fields.CharField')(max_length=36, db_index=True)),
            ('producer', self.gf('django.db.models.fields.CharField')(default='mac-bhp066', max_length=50, db_index=True)),
            ('action', self.gf('django.db.models.fields.CharField')(default='I', max_length=1)),
            ('timestamp', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, db_index=True)),
            ('consumed_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('consumer', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=25, null=True, blank=True)),
            ('is_ignored', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('is_error', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('error', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True, blank=True)),
            ('batch_seq', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('batch_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('is_consumed_middleman', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('is_consumed_server', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal('sync', ['MiddleManTransaction'])

        # Adding model 'Producer'
        db.create_table('bhp_sync_producer', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('user_created', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('user_modified', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('hostname_created', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('hostname_modified', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('revision', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('settings_key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('producer_ip', self.gf('django.db.models.fields.CharField')(max_length=78L, null=True, db_index=True)),
            ('db_user', self.gf('django.db.models.fields.CharField')(default='root', max_length=78L, null=True, db_index=True)),
            ('db_user_name', self.gf('django.db.models.fields.CharField')(max_length=78L, null=True, db_index=True)),
            ('port', self.gf('django.db.models.fields.CharField')(default='', max_length=78L, null=True, blank=True)),
            ('db_password', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, db_index=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('sync_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('sync_status', self.gf('django.db.models.fields.CharField')(default='-', max_length=250, null=True)),
            ('json_limit', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('json_total_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('comment', self.gf('django.db.models.fields.TextField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('sync', ['Producer'])

        # Adding unique constraint on 'Producer', fields ['settings_key', 'is_active']
        db.create_unique('bhp_sync_producer', ['settings_key', 'is_active'])

        # Adding model 'RequestLog'
        db.create_table('bhp_sync_requestlog', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('user_created', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('user_modified', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('hostname_created', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('hostname_modified', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('revision', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('producer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sync.Producer'])),
            ('request_datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 11, 17, 0, 0))),
            ('status', self.gf('django.db.models.fields.CharField')(default='complete', max_length=25)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('sync', ['RequestLog'])

        # Adding model 'TestItem'
        db.create_table('bhp_sync_testitem', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('user_created', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('user_modified', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('hostname_created', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('hostname_modified', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('revision', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('test_item_identifier', self.gf('django.db.models.fields.CharField')(unique=True, max_length=35)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
        ))
        db.send_create_signal('sync', ['TestItem'])


    def backwards(self, orm):
        # Removing unique constraint on 'Producer', fields ['settings_key', 'is_active']
        db.delete_unique('bhp_sync_producer', ['settings_key', 'is_active'])

        # Deleting model 'IncomingTransaction'
        db.delete_table('bhp_sync_incomingtransaction')

        # Deleting model 'OutgoingTransaction'
        db.delete_table('bhp_sync_outgoingtransaction')

        # Deleting model 'MiddleManTransaction'
        db.delete_table('bhp_sync_middlemantransaction')

        # Deleting model 'Producer'
        db.delete_table('bhp_sync_producer')

        # Deleting model 'RequestLog'
        db.delete_table('bhp_sync_requestlog')

        # Deleting model 'TestItem'
        db.delete_table('bhp_sync_testitem')


    models = {
        'sync.incomingtransaction': {
            'Meta': {'ordering': "['timestamp']", 'object_name': 'IncomingTransaction', 'db_table': "'bhp_sync_incomingtransaction'"},
            'action': ('django.db.models.fields.CharField', [], {'default': "'I'", 'max_length': '1'}),
            'batch_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'batch_seq': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'consumed_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'consumer': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'error': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'hostname_created': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'hostname_modified': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'is_consumed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_error': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_ignored': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_self': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'producer': ('django.db.models.fields.CharField', [], {'default': "'mac-bhp066'", 'max_length': '50', 'db_index': 'True'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'db_index': 'True'}),
            'tx': ('django.db.models.fields.TextField', [], {}),
            'tx_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'tx_pk': ('django.db.models.fields.CharField', [], {'max_length': '36', 'db_index': 'True'}),
            'user_created': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'}),
            'user_modified': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'})
        },
        'sync.middlemantransaction': {
            'Meta': {'ordering': "['timestamp']", 'object_name': 'MiddleManTransaction', 'db_table': "'bhp_sync_middlemantransaction'"},
            'action': ('django.db.models.fields.CharField', [], {'default': "'I'", 'max_length': '1'}),
            'batch_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'batch_seq': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'consumed_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'consumer': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'error': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'hostname_created': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'hostname_modified': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'is_consumed_middleman': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_consumed_server': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_error': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_ignored': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'producer': ('django.db.models.fields.CharField', [], {'default': "'mac-bhp066'", 'max_length': '50', 'db_index': 'True'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'db_index': 'True'}),
            'tx': ('django.db.models.fields.TextField', [], {}),
            'tx_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'tx_pk': ('django.db.models.fields.CharField', [], {'max_length': '36', 'db_index': 'True'}),
            'user_created': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'}),
            'user_modified': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'})
        },
        'sync.outgoingtransaction': {
            'Meta': {'ordering': "['timestamp']", 'object_name': 'OutgoingTransaction', 'db_table': "'bhp_sync_outgoingtransaction'"},
            'action': ('django.db.models.fields.CharField', [], {'default': "'I'", 'max_length': '1'}),
            'batch_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'batch_seq': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'consumed_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'consumer': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'error': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'hostname_created': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'hostname_modified': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'is_consumed_middleman': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_consumed_server': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_error': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_ignored': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'producer': ('django.db.models.fields.CharField', [], {'default': "'mac-bhp066'", 'max_length': '50', 'db_index': 'True'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'db_index': 'True'}),
            'tx': ('django.db.models.fields.TextField', [], {}),
            'tx_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'tx_pk': ('django.db.models.fields.CharField', [], {'max_length': '36', 'db_index': 'True'}),
            'user_created': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'}),
            'user_modified': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'})
        },
        'sync.producer': {
            'Meta': {'ordering': "['name']", 'unique_together': "(('settings_key', 'is_active'),)", 'object_name': 'Producer', 'db_table': "'bhp_sync_producer'"},
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'db_password': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'db_index': 'True'}),
            'db_user': ('django.db.models.fields.CharField', [], {'default': "'root'", 'max_length': '78L', 'null': 'True', 'db_index': 'True'}),
            'db_user_name': ('django.db.models.fields.CharField', [], {'max_length': '78L', 'null': 'True', 'db_index': 'True'}),
            'hostname_created': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'hostname_modified': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'json_limit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'json_total_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'port': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '78L', 'null': 'True', 'blank': 'True'}),
            'producer_ip': ('django.db.models.fields.CharField', [], {'max_length': '78L', 'null': 'True', 'db_index': 'True'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'settings_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'sync_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'sync_status': ('django.db.models.fields.CharField', [], {'default': "'-'", 'max_length': '250', 'null': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'user_created': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'}),
            'user_modified': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'})
        },
        'sync.requestlog': {
            'Meta': {'object_name': 'RequestLog', 'db_table': "'bhp_sync_requestlog'"},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'hostname_created': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'hostname_modified': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'producer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sync.Producer']"}),
            'request_datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 11, 17, 0, 0)'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'complete'", 'max_length': '25'}),
            'user_created': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'}),
            'user_modified': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'})
        },
        'sync.testitem': {
            'Meta': {'object_name': 'TestItem', 'db_table': "'bhp_sync_testitem'"},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'hostname_created': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'hostname_modified': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'test_item_identifier': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '35'}),
            'user_created': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'}),
            'user_modified': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'})
        }
    }

    complete_apps = ['sync']