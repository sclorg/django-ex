# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20170131_0004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='bceid',
            field=models.CharField(db_index=True, max_length=100),
        ),
    ]
