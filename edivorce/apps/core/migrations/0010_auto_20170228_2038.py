# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bceiduser',
            name='user_guid',
            field=models.CharField(max_length=200, db_index=True, unique=True),
        ),
    ]
