# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20170321_2201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='summary_order',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
