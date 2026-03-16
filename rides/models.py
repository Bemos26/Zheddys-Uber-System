from django.db import models
from django.conf import settings

class Vehicle(models.Model):
    rider = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehicle')
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    license_plate = models.CharField(max_length=20, unique=True)
    color = models.CharField(max_length=30)
    
    def __str__(self):
        return f"{self.make} {self.model} ({self.license_plate})"

class Location(models.Model):
    rider = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='location')
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_online = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.rider.username} - {self.latitude}, {self.longitude}"

class Trip(models.Model):
    STATUS_CHOICES = (
        ('REQUESTED', 'Requested'),
        ('ACCEPTED', 'Accepted'),
        ('EN_ROUTE', 'En Route'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELED', 'Canceled'),
    )
    
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trips_as_passenger')
    rider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='trips_as_rider')
    
    # Store coordinates as simple floats for SQLite MVP
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    
    pickup_address = models.CharField(max_length=255)
    dropoff_address = models.CharField(max_length=255)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REQUESTED')
    fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Trip {self.id} - {self.status}"
