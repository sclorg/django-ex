# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20170210_1702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bceiduser',
            name='user_guid',
            field=models.CharField(max_length=50, unique=True, db_index=True),
        ),
    ]
