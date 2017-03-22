# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20170321_2237'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='conditional_target',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='question',
            name='required',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='question',
            name='reveal_response',
            field=models.TextField(blank=True),
        ),
    ]
