# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20171114_2151'),
    ]

    operations = [
        migrations.AddField(
            model_name='bceiduser',
            name='has_seen_orders_page',
            field=models.BooleanField(default=False),
        ),
    ]
