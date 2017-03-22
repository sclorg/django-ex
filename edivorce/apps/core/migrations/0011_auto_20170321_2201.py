# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20170228_2038'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ('summary_order',)},
        ),
        migrations.AddField(
            model_name='question',
            name='summary_order',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
