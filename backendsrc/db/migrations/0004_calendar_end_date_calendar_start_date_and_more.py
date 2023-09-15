# Generated by Django 4.2.4 on 2023-09-15 04:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0003_station_suburb"),
    ]

    operations = [
        migrations.AddField(
            model_name="calendar",
            name="end_date",
            field=models.DateField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name="calendar",
            name="start_date",
            field=models.DateField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name="station",
            name="suburb",
            field=models.CharField(max_length=255, null=True),
        ),
    ]
