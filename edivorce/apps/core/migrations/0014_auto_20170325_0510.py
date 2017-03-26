# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20170322_2055'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='formquestions',
            name='legal_form',
        ),
        migrations.RemoveField(
            model_name='formquestions',
            name='question',
        ),
        migrations.RemoveField(
            model_name='legalform',
            name='questions',
        ),
        migrations.DeleteModel(
            name='FormQuestions',
        ),
        migrations.DeleteModel(
            name='LegalForm',
        ),
    ]
