# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import files.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Directory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dir_name', models.CharField(max_length=150)),
                ('hash', models.CharField(default=files.models.Directory._createDirHash, max_length=25, unique=True)),
                ('created_t', models.DateTimeField()),
                ('full_path', models.CharField(max_length=150)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('parent_id', models.ForeignKey(to='files.Directory', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DirShares',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_t', models.DateTimeField()),
                ('share_id', models.ForeignKey(to='files.Directory')),
                ('shared_with', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('download_hash', models.CharField(default=files.models.File._createDownloadHash, max_length=25, unique=True)),
                ('created_t', models.DateTimeField()),
                ('dir_id', models.ForeignKey(to='files.Directory')),
            ],
        ),
        migrations.CreateModel(
            name='FileShares',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_t', models.DateTimeField()),
                ('share_id', models.ForeignKey(to='files.File')),
                ('shared_with', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FileStorage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_hash', models.CharField(default=files.models.FileStorage._createHash, max_length=15, unique=True)),
                ('name', models.CharField(max_length=15)),
                ('file_type', models.CharField(default='UNKNOWN_TYPE', max_length=25)),
                ('size', models.BigIntegerField()),
                ('upload_t', models.DateTimeField()),
                ('counter', models.IntegerField(default=1)),
                ('orig_owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='file',
            name='file_id',
            field=models.ForeignKey(to='files.FileStorage'),
        ),
        migrations.AddField(
            model_name='file',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
