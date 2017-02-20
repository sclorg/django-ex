# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FormQuestions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transformation', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='LegalForm',
            fields=[
                ('key', models.TextField(serialize=False, primary_key=True)),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bceid', models.CharField(max_length=100)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('key', models.TextField(serialize=False, primary_key=True)),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField(blank=True)),
                ('question', models.ForeignKey(to='core.Question')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='legalform',
            name='questions',
            field=models.ManyToManyField(to='core.Question', through='core.FormQuestions'),
        ),
        migrations.AddField(
            model_name='formquestions',
            name='legal_form',
            field=models.ForeignKey(to='core.LegalForm'),
        ),
        migrations.AddField(
            model_name='formquestions',
            name='question',
            field=models.ForeignKey(to='core.Question'),
        ),
    ]
