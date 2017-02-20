# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_legalform_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='name',
            field=models.TextField(blank=True),
        ),
    ]
