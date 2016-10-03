# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repeat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='list',
            name='status',
            field=models.CharField(choices=[('e', 'Empty'), ('n', 'Normal'), ('h', 'Hard'), ('s', 'Simple'), ('o', 'Old')], max_length=1, default='e'),
        ),
    ]
