# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-01 09:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio_manager', '0012_auto_20161201_1130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
