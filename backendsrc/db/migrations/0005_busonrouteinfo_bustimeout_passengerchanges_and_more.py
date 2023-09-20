# Generated by Django 4.2.5 on 2023-09-16 08:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0004_calendar_end_date_calendar_start_date_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="BusOnRouteInfo",
            fields=[
                (
                    "bus_id",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BusTimeOut",
            fields=[
                (
                    "bustimeout_id",
                    models.IntegerField(primary_key=True, serialize=False),
                ),
                ("stop_name", models.CharField(max_length=255)),
                ("time", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="PassengerChanges",
            fields=[
                (
                    "passenger_changes_id",
                    models.IntegerField(primary_key=True, serialize=False),
                ),
                ("time", models.IntegerField()),
                ("passenger_count", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="StationSim",
            fields=[
                (
                    "station_id",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=255)),
                ("lat", models.FloatField()),
                ("long", models.FloatField()),
                (
                    "passenger_count",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="db.passengerchanges",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RouteSim",
            fields=[
                (
                    "route_id",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                ("method", models.CharField(max_length=255)),
                (
                    "buses_on_route",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="db.busonrouteinfo",
                    ),
                ),
                (
                    "stations",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="db.stationsim"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ItinerarySim",
            fields=[
                (
                    "itinerary_id",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                (
                    "routes",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="db.routesim"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="busonrouteinfo",
            name="bus_passenger_changes",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="db.passengerchanges"
            ),
        ),
        migrations.AddField(
            model_name="busonrouteinfo",
            name="bus_timeout",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="db.bustimeout"
            ),
        ),
        migrations.AddField(
            model_name="simulationoutput",
            name="itinerary_id",
            field=models.ForeignKey(
                default=-1,
                on_delete=django.db.models.deletion.CASCADE,
                to="db.itinerarysim",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="simulationoutput",
            name="route_id",
            field=models.ForeignKey(
                default=-1,
                on_delete=django.db.models.deletion.CASCADE,
                to="db.routesim",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="simulationoutput",
            name="station_id",
            field=models.ForeignKey(
                default=-1,
                on_delete=django.db.models.deletion.CASCADE,
                to="db.stationsim",
            ),
            preserve_default=False,
        ),
    ]
