from rest_framework import serializers
from db.models import Station


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ['station_id','name','lat','long']