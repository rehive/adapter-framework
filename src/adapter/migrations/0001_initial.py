# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-09 14:06
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('type', models.CharField(blank=True, max_length=100, null=True)),
                ('secret', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, null=True)),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, null=True)),
                ('default', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rehive_code', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('external_id', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('tx_type', models.CharField(choices=[('deposit', 'Deposit'), ('withdraw', 'Withdraw')], max_length=50)),
                ('to_reference', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('from_reference', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('amount', models.BigIntegerField(default=0)),
                ('fee', models.BigIntegerField(default=0)),
                ('currency', models.CharField(max_length=12)),
                ('status', models.CharField(blank=True, choices=[('Waiting', 'Waiting'), ('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Complete', 'Complete'), ('Failed', 'Failed'), ('Cancelled', 'Cancelled')], max_length=24, null=True)),
                ('note', models.TextField(blank=True, default='', max_length=100, null=True)),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, null=True)),
                ('rehive_response', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, null=True)),
                ('created', models.DateTimeField()),
                ('updated', models.DateTimeField()),
                ('completed', models.DateTimeField(blank=True, null=True)),
                ('admin_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adapter.AdminAccount')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=200, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=30, null=True)),
                ('last_name', models.CharField(blank=True, max_length=30, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('mobile_number', models.CharField(blank=True, max_length=24, null=True)),
                ('created', models.DateTimeField()),
                ('updated', models.DateTimeField()),
            ],
        ),
        migrations.AddField(
            model_name='transaction',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='adapter.User'),
        ),
    ]
