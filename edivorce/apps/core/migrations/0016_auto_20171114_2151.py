# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20170330_0522'),
    ]

    operations = [
        migrations.AddField(
            model_name='bceiduser',
            name='display_name',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='bceiduser',
            name='sm_user',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='userresponse',
            name='bceid_user',
            field=models.ForeignKey(related_name='responses', to='core.BceidUser'),
        ),
        migrations.AlterField(
            model_name='userresponse',
            name='question',
            field=models.ForeignKey(related_name='responses', to='core.Question'),
        ),
    ]
