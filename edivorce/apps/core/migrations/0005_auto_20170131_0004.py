# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0004_auto_20170112_2003'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField(blank=True)),
                ('question', models.ForeignKey(to='core.Question')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='response',
            name='question',
        ),
        migrations.RemoveField(
            model_name='response',
            name='user',
        ),
        migrations.DeleteModel(
            name='Response',
        ),
    ]
