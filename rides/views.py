from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Vehicle, Trip
from .serializers import VehicleSerializer, TripSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Vehicle.objects.all()
        return Vehicle.objects.filter(rider=self.request.user)

    def perform_create(self, serializer):
        serializer.save(rider=self.request.user)

class TripViewSet(viewsets.ModelViewSet):
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Trip.objects.all()
        elif user.role == 'rider':
            return Trip.objects.filter(rider=user)
        else: # passenger
            return Trip.objects.filter(passenger=user)

    def perform_create(self, serializer):
        # Only passengers can request rides directly
        if self.request.user.role == 'passenger':
            serializer.save(passenger=self.request.user)
        else:
            raise permissions.PermissionDenied("Only passengers can request a ride.")

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        trip = self.get_object()
        user = request.user
        
        if user.role != 'rider':
            return Response({'error': 'Only riders can accept trips.'}, status=status.HTTP_403_FORBIDDEN)
        if trip.status != 'REQUESTED':
            return Response({'error': 'Trip is not available.'}, status=status.HTTP_400_BAD_REQUEST)
            
        trip.rider = user
        trip.status = 'ACCEPTED'
        trip.save()
        return Response(TripSerializer(trip).data)

    @action(detail=True, methods=['post'])
    def arrive(self, request, pk=None):
        trip = self.get_object()
        if trip.rider != request.user or trip.status != 'ACCEPTED':
            return Response({'error': 'Invalid operation.'}, status=status.HTTP_400_BAD_REQUEST)
            
        trip.status = 'EN_ROUTE'
        trip.save()
        return Response(TripSerializer(trip).data)
        
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        trip = self.get_object()
        if trip.rider != request.user or trip.status != 'EN_ROUTE':
            return Response({'error': 'Invalid operation.'}, status=status.HTTP_400_BAD_REQUEST)
            
        trip.status = 'IN_PROGRESS'
        trip.save()
        return Response(TripSerializer(trip).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        trip = self.get_object()
        if trip.rider != request.user or trip.status != 'IN_PROGRESS':
            return Response({'error': 'Invalid operation.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Basic MVP Fare Calculation (Euclidean distance * Base Rate)
        # In production, use PostGIS distance or Google Maps API
        import math
        dx = trip.dropoff_latitude - trip.pickup_latitude
        dy = trip.dropoff_longitude - trip.pickup_longitude
        distance_deg = math.sqrt(dx*dx + dy*dy)
        distance_km = distance_deg * 111 # rough approximation
        
        base_fare = 50.0  # e.g., 50 KES base
        rate_per_km = 30.0 # 30 KES per km
        total_fare = base_fare + (distance_km * rate_per_km)
        
        trip.status = 'COMPLETED'
        trip.completed_at = timezone.now()
        trip.fare = round(total_fare, 2)
        trip.save()
        return Response(TripSerializer(trip).data)
