# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-05-02 17:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TAHiring', '0003_auto_20170502_1732'),
    ]

    operations = [
        migrations.AddField(
            model_name='tacourseinterest',
            name='is_new',
            field=models.BooleanField(default=False),
        ),
    ]