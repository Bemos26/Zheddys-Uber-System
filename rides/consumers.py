import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from .models import Location

User = get_user_model()

class RideConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        # In a real app, only authenticated users can connect. 
        # For simplicity in testing, we accept all for now but check if authenticated
        if self.user.is_authenticated:
            if self.user.role == 'rider':
                self.group_name = f'rider_{self.user.id}'
            else:
                self.group_name = f'passenger_{self.user.id}'
            
            # Join the user-specific group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            # Riders also join a global "available_riders" group
            if self.user.role == 'rider':
                await self.channel_layer.group_add(
                    'available_riders',
                    self.channel_name
                )

            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            
            if self.user.role == 'rider':
                await self.channel_layer.group_discard(
                    'available_riders',
                    self.channel_name
                )
                
                # Mark Rider offline (sync to async needed for DB call)
                await self.set_rider_offline()


    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'update_location' and self.user.role == 'rider':
            lat = data.get('latitude')
            lon = data.get('longitude')
            await self.update_rider_location(lat, lon)
            
            # Send acknowledgment back to the rider
            await self.send(text_data=json.dumps({
                'type': 'location_updated',
                'status': 'success'
            }))
            
        elif action == 'request_ride' and self.user.role == 'passenger':
            # Broadcast to all available riders (simplified approach, ideally we filter by distance)
            payload = {
                'type': 'ride_requested',
                'passenger_id': self.user.id,
                'passenger_name': self.user.username,
                'pickup': data.get('pickup'),
                'dropoff': data.get('dropoff'),
                'trip_id': data.get('trip_id')
            }
            
            await self.channel_layer.group_send(
                'available_riders',
                payload
            )

    # Handlers for messages sent over the channel layer
    async def ride_requested(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def update_rider_location(self, lat, lon):
        Location.objects.update_or_create(
            rider=self.user,
            defaults={'latitude': lat, 'longitude': lon, 'is_online': True}
        )

    @sync_to_async
    def set_rider_offline(self):
        Location.objects.filter(rider=self.user).update(is_online=False)
