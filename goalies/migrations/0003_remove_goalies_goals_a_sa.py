# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-18 02:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('goalies', '0002_auto_20170914_1630'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goalies',
            name='goals_a_sa',
        ),
    ]