# Generated by Django 4.2.4 on 2023-09-20 07:52

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BusOnRouteInfo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("bus_id", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Calendar",
            fields=[
                (
                    "service_id",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                ("monday", models.BooleanField(default=False)),
                ("tuesday", models.BooleanField(default=False)),
                ("wednesday", models.BooleanField(default=False)),
                ("thursday", models.BooleanField(default=False)),
                ("friday", models.BooleanField(default=False)),
                ("saturday", models.BooleanField(default=False)),
                ("sunday", models.BooleanField(default=False)),
                ("start_date", models.DateField(default=datetime.datetime.now)),
                ("end_date", models.DateField(default=datetime.datetime.now)),
            ],
            options={
                "ordering": ["service_id"],
            },
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
            name="Route",
            fields=[
                (
                    "route_id",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=255)),
                ("transport_type", models.IntegerField()),
                ("capacity", models.IntegerField(null=True)),
            ],
            options={
                "ordering": ["route_id"],
            },
        ),
        migrations.CreateModel(
            name="Shape",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("shape_id", models.CharField(max_length=255)),
                ("shape_pt_lat", models.FloatField()),
                ("shape_pt_lon", models.FloatField()),
                ("shape_pt_sequence", models.IntegerField()),
            ],
            options={
                "ordering": ["shape_id", "shape_pt_sequence"],
                "unique_together": {("shape_id", "shape_pt_sequence")},
            },
        ),
        migrations.CreateModel(
            name="SimulationOutput",
            fields=[
                (
                    "simulation_id",
                    models.IntegerField(primary_key=True, serialize=False),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Station",
            fields=[
                (
                    "station_id",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                ("station_code", models.CharField(max_length=255)),
                ("name", models.CharField(max_length=255)),
                ("lat", models.FloatField()),
                ("long", models.FloatField()),
                ("location_type", models.IntegerField()),
                ("suburb", models.CharField(max_length=255, null=True)),
            ],
            options={
                "ordering": ["station_id"],
            },
        ),
        migrations.CreateModel(
            name="Trip",
            fields=[
                (
                    "trip_id",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                (
                    "route_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="db.route"
                    ),
                ),
                (
                    "service_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="db.calendar"
                    ),
                ),
                (
                    "shape_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="db.shape"
                    ),
                ),
            ],
            options={
                "ordering": ["trip_id", "route_id", "service_id", "shape_id"],
            },
        ),
        migrations.CreateModel(
            name="TravelTimes",
            fields=[
                (
                    "traveltime_id",
                    models.IntegerField(primary_key=True, serialize=False),
                ),
                ("duration", models.FloatField(default=0)),
                (
                    "from_station",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="from_station",
                        to="db.station",
                    ),
                ),
                (
                    "to_station",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="to_station",
                        to="db.station",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="StationSim",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("station_id", models.CharField(max_length=255)),
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
                (
                    "sim_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="db.simulationoutput",
                    ),
                ),
            ],
            options={
                "unique_together": {("sim_id", "station_id", "passenger_count")},
            },
        ),
        migrations.CreateModel(
            name="RouteSim",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("route_id", models.CharField(max_length=255)),
                ("method", models.CharField(max_length=255)),
                (
                    "buses_on_route",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="db.busonrouteinfo",
                    ),
                ),
                (
                    "sim_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="db.simulationoutput",
                    ),
                ),
                (
                    "stations",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="db.stationsim"
                    ),
                ),
            ],
            options={
                "unique_together": {
                    ("sim_id", "route_id", "buses_on_route", "stations")
                },
            },
        ),
        migrations.AddField(
            model_name="passengerchanges",
            name="sim_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="db.simulationoutput"
            ),
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
                (
                    "sim_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="db.simulationoutput",
                    ),
                ),
            ],
            options={
                "unique_together": {("bustimeout_id", "sim_id", "time")},
            },
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
            model_name="busonrouteinfo",
            name="sim_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="db.simulationoutput"
            ),
        ),
        migrations.CreateModel(
            name="Timetable",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("arrival_time", models.TimeField(max_length=255)),
                ("sequence", models.IntegerField()),
                (
                    "station",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="db.station",
                    ),
                ),
                (
                    "trip_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="db.trip"
                    ),
                ),
            ],
            options={
                "ordering": ["trip_id"],
                "unique_together": {("trip_id", "station", "arrival_time", "sequence")},
            },
        ),
        migrations.AlterUniqueTogether(
            name="passengerchanges",
            unique_together={("passenger_changes_id", "sim_id", "time")},
        ),
        migrations.CreateModel(
            name="ItinerarySim",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("itinerary_id", models.CharField(max_length=255)),
                (
                    "routes",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="db.routesim"
                    ),
                ),
                (
                    "sim_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="db.simulationoutput",
                    ),
                ),
            ],
            options={
                "unique_together": {("sim_id", "itinerary_id")},
            },
        ),
        migrations.AlterUniqueTogether(
            name="busonrouteinfo",
            unique_together={
                ("bus_id", "sim_id", "bus_timeout", "bus_passenger_changes")
            },
        ),
    ]
