# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-05-10 16:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TAHiring', '0002_auto_20170509_1654'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['course_code', 'term'], 'verbose_name': 'Course'},
        ),
        migrations.AlterModelOptions(
            name='coursetutorial',
            options={'ordering': ['course', 'name', 'timeslot'], 'verbose_name': 'Tutorial'},
        ),
        migrations.AddField(
            model_name='coursetutorial',
            name='term',
            field=models.CharField(choices=[('F', 'Fall'), ('S', 'Spring'), ('Y', 'Full Year'), ('U', 'Summer')], default='F', max_length=1),
        ),
    ]
