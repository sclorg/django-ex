# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20170111_2157'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='formquestions',
            options={'verbose_name_plural': 'Form Questions'},
        ),
        migrations.AlterModelOptions(
            name='legalform',
            options={'ordering': ('order',), 'verbose_name_plural': 'Legal Forms'},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ('key',)},
        ),
    ]
