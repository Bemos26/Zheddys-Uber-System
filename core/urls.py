from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('passenger/', views.passenger_view, name='passenger_dashboard'),
    path('rider/', views.rider_view, name='rider_dashboard'),
]
