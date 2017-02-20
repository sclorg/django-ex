# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20170209_1858'),
    ]

    operations = [
        migrations.CreateModel(
            name='BceidUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_guid', models.CharField(unique=True, max_length=36, db_index=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.RemoveField(
            model_name='profile',
            name='user',
        ),
        migrations.RemoveField(
            model_name='userresponse',
            name='user',
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
        migrations.AddField(
            model_name='userresponse',
            name='bceid_user',
            field=models.ForeignKey(default=1, to='core.BceidUser'),
            preserve_default=False,
        ),
    ]
