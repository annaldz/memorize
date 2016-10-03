# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repeat', '0002_list_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='list',
            name='status',
            field=models.CharField(choices=[('e', 'Empty'), ('n', 'Normal'), ('h', 'Hard'), ('s', 'Simple'), ('o', 'Old'), ('x', 'Extra_old')], max_length=1, default='e'),
        ),
    ]
