# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-05-05 21:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('TAHiring', '0006_auto_20170504_1924'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='course_tutorial',
            options={'ordering': ['timeslot'], 'verbose_name': 'Tutorial'},
        ),
        migrations.AlterModelOptions(
            name='taavailability',
            options={'ordering': ['ta', 'timeslot'], 'verbose_name': 'TA Availability', 'verbose_name_plural': 'TA Availabilities'},
        ),
        migrations.AlterModelOptions(
            name='timeslot',
            options={'ordering': ['day_of_week', 'time_of_day']},
        ),
    ]
