from rest_framework import viewsets, permissions
from .models import Vehicle
from .serializers import VehicleSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # A rider can only see/manage their own vehicle. Admin sees all.
        if self.request.user.role == 'admin':
            return Vehicle.objects.all()
        return Vehicle.objects.filter(rider=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the logged-in rider to the vehicle
        serializer.save(rider=self.request.user)
