# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20160906_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='image',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
