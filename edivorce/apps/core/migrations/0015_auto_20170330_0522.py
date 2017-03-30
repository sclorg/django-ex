# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20170325_0510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bceiduser',
            name='user_guid',
            field=models.CharField(db_index=True, unique=True, max_length=32),
        ),
    ]
