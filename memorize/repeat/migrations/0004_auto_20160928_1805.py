# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('repeat', '0003_auto_20160909_1437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flashcard',
            name='question',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='list',
            name='limit',
            field=models.PositiveIntegerField(default=30, validators=[django.core.validators.MaxValueValidator(500), django.core.validators.MinValueValidator(5)]),
        ),
    ]
