from django.contrib import admin
from .models import Vehicle, Location, Trip

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('rider', 'make', 'model', 'license_plate')
    search_fields = ('license_plate', 'rider__username')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('rider', 'latitude', 'longitude', 'is_online', 'updated_at')
    list_filter = ('is_online',)

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('id', 'passenger', 'rider', 'status', 'fare', 'created_at')
    list_filter = ('status',)
    search_fields = ('passenger__username', 'rider__username')
