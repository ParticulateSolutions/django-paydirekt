# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PaydirektCapture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(verbose_name='amount', max_digits=9, decimal_places=2)),
                ('transaction_id', models.CharField(unique=True, max_length=255, verbose_name='transaction id')),
                ('final', models.BooleanField(default=False, verbose_name='final')),
                ('link', models.URLField(verbose_name='link')),
                ('status', models.CharField(max_length=255, verbose_name='status', blank=True)),
                ('capture_type', models.CharField(max_length=255, verbose_name='capture type', blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='last modified')),
            ],
            options={
                'verbose_name': 'Paydirekt Capture',
                'verbose_name_plural': 'Paydirekt Captures',
            },
        ),
        migrations.CreateModel(
            name='PaydirektCheckout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('checkout_id', models.CharField(unique=True, max_length=255, verbose_name='checkout id')),
                ('payment_type', models.CharField(max_length=255, verbose_name='payment type')),
                ('total_amount', models.DecimalField(verbose_name='total amount', max_digits=9, decimal_places=2)),
                ('status', models.CharField(max_length=255, verbose_name='status', blank=True)),
                ('link', models.URLField(verbose_name='link')),
                ('approve_link', models.URLField(verbose_name='approve link')),
                ('close_link', models.URLField(verbose_name='close link', blank=True)),
                ('captures_link', models.URLField(verbose_name='captures link', blank=True)),
                ('refunds_link', models.URLField(verbose_name='refunds link', blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='last modified')),
            ],
            options={
                'verbose_name': 'Paydirekt Checkout',
                'verbose_name_plural': 'Paydirekt Checkouts',
            },
        ),
        migrations.CreateModel(
            name='PaydirektRefund',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(verbose_name='amount', max_digits=9, decimal_places=2)),
                ('transaction_id', models.CharField(unique=True, max_length=255, verbose_name='transaction id')),
                ('link', models.URLField(verbose_name='link')),
                ('status', models.CharField(max_length=255, verbose_name='status', blank=True)),
                ('refund_type', models.CharField(max_length=255, verbose_name='refund type', blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('checkout', models.ForeignKey(related_name='refunds', verbose_name='checkout', to='django_paydirekt.PaydirektCheckout')),
            ],
            options={
                'verbose_name': 'Paydirekt Refund',
                'verbose_name_plural': 'Paydirekt Refund',
            },
        ),
        migrations.AddField(
            model_name='paydirektcapture',
            name='checkout',
            field=models.ForeignKey(related_name='captures', verbose_name='checkout', to='django_paydirekt.PaydirektCheckout'),
        ),
    ]
