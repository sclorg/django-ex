# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_bceiduser_has_seen_orders_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='bceiduser',
            name='has_accepted_terms',
            field=models.BooleanField(default=False),
        ),
    ]
