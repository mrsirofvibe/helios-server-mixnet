# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('helios', '0002_auto_20160106_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='castvote',
            name='cast_from',
            field=models.GenericIPAddressField(null=True),
            preserve_default=True,
        ),
    ]
