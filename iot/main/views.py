from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django import forms
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from .models import Solar_Panel, Characteristics
import logging
from django.core import serializers
import requests
import json
SERVER_URL = 'http://127.0.0.1:8080'  # адрес сервера
from django.views.generic import TemplateView


def dashboard(request):
    solar_panels = Solar_Panel.objects.all()

    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        selected_panel_number = request.GET.get('selected_panel')
        if selected_panel_number == "all":
            characteristics = Characteristics.objects.all().order_by('-date', 'time')
        else:
            selected_panel = Solar_Panel.objects.get(installation_number=selected_panel_number)
            characteristics = Characteristics.objects.filter(solar_panel=selected_panel).order_by('-date', 'time')

        # Serializing queryset to JSON
        data = serializers.serialize('json', characteristics)
        return JsonResponse({'data': data})

    return render(request, 'dashboard.html', {'solar_panels': solar_panels})


def get_characteristics_data(request, installation_number):
    characteristics = Characteristics.objects.filter(solar_panel__installation_number=installation_number).order_by('-date', 'time')
    data = {
        'labels': [f"{char.date} {char.time}" for char in characteristics],
        'generated_power_data': [char.generated_power for char in characteristics],
        # ... add other data as needed
    }
    return JsonResponse(data)


def char_table(request):
    char = Characteristics.objects.order_by('-date', '-time') 
    return render(request, "table.html", {'characteristics': char})


def solar_panels(request):
    solar = Solar_Panel.objects.all()
    return render(request, "panels.html", {'panels': solar})


def characteristics_data(request):
    # Get the selected solar panel if provided
    selected_panel_id = request.GET.get('solar_panel')
    if selected_panel_id:
        characteristics = Characteristics.objects.filter(solar_panel_id=selected_panel_id)
    else:
        characteristics = Characteristics.objects.all()

    # Prepare the data for the response
    data = {
        'dates': [char.date.strftime("%Y-%m-%d") for char in characteristics],
        'generated_power': [char.generated_power for char in characteristics],
        'consumed_power': [char.consumed_power for char in characteristics],
    }

    return JsonResponse(data)


def socket(request):
    sol = Solar_Panel.objects.all()
    return render(request, "socket.html")


# функции сервера
def get_connected_clients(request):
    response = requests.get(f"{SERVER_URL}/clients")
    if response.ok:
        return JsonResponse(response.json())
    else:
        return JsonResponse({"error": "Ошибка при получении списка клиентов"}, status=500)

def set_active_client(request):
    client_id = request.POST.get('client_id')
    response = requests.post(f"{SERVER_URL}/set_active_client", json={"client_id": client_id})
    if response.ok:
        return JsonResponse({"message": "Активный клиент установлен"})
    else:
        return JsonResponse({"error": "Ошибка при установке активного клиента"}, status=500)

def send_message_to_client(request):
    message = request.POST.get('message')
    response = requests.post(f"{SERVER_URL}/send_message", json={"message": message})
    if response.ok:
        return JsonResponse({"message": "Сообщение отправлено"})
    else:
        return JsonResponse({"error": "Ошибка при отправке сообщения"}, status=500)