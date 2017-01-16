# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-12 04:02
from __future__ import unicode_literals

from django.db import migrations, models
import edc_base.model.fields.hostname_modification_field
import edc_base.model.fields.userfield
import edc_base.utils


class Migration(migrations.Migration):

    dependencies = [
        ('edc_sync', '0007_auto_20161128_0044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='created',
            field=models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow),
        ),
        migrations.AlterField(
            model_name='client',
            name='hostname_created',
            field=models.CharField(blank=True, default='mac2-2.local', help_text='System field. (modified on create only)', max_length=50),
        ),
        migrations.AlterField(
            model_name='client',
            name='hostname_modified',
            field=edc_base.model.fields.hostname_modification_field.HostnameModificationField(blank=True, help_text='System field. (modified on every save)', max_length=50),
        ),
        migrations.AlterField(
            model_name='client',
            name='modified',
            field=models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow),
        ),
        migrations.AlterField(
            model_name='client',
            name='user_created',
            field=edc_base.model.fields.userfield.UserField(blank=True, max_length=50, verbose_name='user created'),
        ),
        migrations.AlterField(
            model_name='client',
            name='user_modified',
            field=edc_base.model.fields.userfield.UserField(blank=True, max_length=50, verbose_name='user modified'),
        ),
        migrations.AlterField(
            model_name='history',
            name='created',
            field=models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow),
        ),
        migrations.AlterField(
            model_name='history',
            name='hostname_created',
            field=models.CharField(blank=True, default='mac2-2.local', help_text='System field. (modified on create only)', max_length=50),
        ),
        migrations.AlterField(
            model_name='history',
            name='hostname_modified',
            field=edc_base.model.fields.hostname_modification_field.HostnameModificationField(blank=True, help_text='System field. (modified on every save)', max_length=50),
        ),
        migrations.AlterField(
            model_name='history',
            name='modified',
            field=models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow),
        ),
        migrations.AlterField(
            model_name='history',
            name='user_created',
            field=edc_base.model.fields.userfield.UserField(blank=True, max_length=50, verbose_name='user created'),
        ),
        migrations.AlterField(
            model_name='history',
            name='user_modified',
            field=edc_base.model.fields.userfield.UserField(blank=True, max_length=50, verbose_name='user modified'),
        ),
        migrations.AlterField(
            model_name='incomingtransaction',
            name='created',
            field=models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow),
        ),
        migrations.AlterField(
            model_name='incomingtransaction',
            name='hostname_created',
            field=models.CharField(blank=True, default='mac2-2.local', help_text='System field. (modified on create only)', max_length=50),
        ),
        migrations.AlterField(
            model_name='incomingtransaction',
            name='hostname_modified',
            field=edc_base.model.fields.hostname_modification_field.HostnameModificationField(blank=True, help_text='System field. (modified on every save)', max_length=50),
        ),
        migrations.AlterField(
            model_name='incomingtransaction',
            name='modified',
            field=models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow),
        ),
        migrations.AlterField(
            model_name='incomingtransaction',
            name='user_created',
            field=edc_base.model.fields.userfield.UserField(blank=True, max_length=50, verbose_name='user created'),
        ),
        migrations.AlterField(
            model_name='incomingtransaction',
            name='user_modified',
            field=edc_base.model.fields.userfield.UserField(blank=True, max_length=50, verbose_name='user modified'),
        ),
        migrations.AlterField(
            model_name='outgoingtransaction',
            name='created',
            field=models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow),
        ),
        migrations.AlterField(
            model_name='outgoingtransaction',
            name='hostname_created',
            field=models.CharField(blank=True, default='mac2-2.local', help_text='System field. (modified on create only)', max_length=50),
        ),
        migrations.AlterField(
            model_name='outgoingtransaction',
            name='hostname_modified',
            field=edc_base.model.fields.hostname_modification_field.HostnameModificationField(blank=True, help_text='System field. (modified on every save)', max_length=50),
        ),
        migrations.AlterField(
            model_name='outgoingtransaction',
            name='modified',
            field=models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow),
        ),
        migrations.AlterField(
            model_name='outgoingtransaction',
            name='user_created',
            field=edc_base.model.fields.userfield.UserField(blank=True, max_length=50, verbose_name='user created'),
        ),
        migrations.AlterField(
            model_name='outgoingtransaction',
            name='user_modified',
            field=edc_base.model.fields.userfield.UserField(blank=True, max_length=50, verbose_name='user modified'),
        ),
        migrations.AlterField(
            model_name='server',
            name='created',
            field=models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow),
        ),
        migrations.AlterField(
            model_name='server',
            name='hostname_created',
            field=models.CharField(blank=True, default='mac2-2.local', help_text='System field. (modified on create only)', max_length=50),
        ),
        migrations.AlterField(
            model_name='server',
            name='hostname_modified',
            field=edc_base.model.fields.hostname_modification_field.HostnameModificationField(blank=True, help_text='System field. (modified on every save)', max_length=50),
        ),
        migrations.AlterField(
            model_name='server',
            name='modified',
            field=models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow),
        ),
        migrations.AlterField(
            model_name='server',
            name='user_created',
            field=edc_base.model.fields.userfield.UserField(blank=True, max_length=50, verbose_name='user created'),
        ),
        migrations.AlterField(
            model_name='server',
            name='user_modified',
            field=edc_base.model.fields.userfield.UserField(blank=True, max_length=50, verbose_name='user modified'),
        ),
    ]
