from django.shortcuts import render

def login_view(request):
    return render(request, 'login.html')

def passenger_view(request):
    return render(request, 'passenger.html')

def rider_view(request):
    return render(request, 'rider.html')
