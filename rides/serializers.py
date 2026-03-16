from rest_framework import serializers
from .models import Vehicle, Location, Trip

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'
        read_only_fields = ('rider',)

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
        read_only_fields = ('rider', 'updated_at')

class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = '__all__'
        read_only_fields = ('passenger', 'rider', 'status', 'fare', 'created_at', 'updated_at', 'completed_at')
