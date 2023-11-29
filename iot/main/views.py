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
from django.views.generic import TemplateView, View


class DashboardView(View):
    def get(self, request, *args, **kwargs):
        solar_panels = Solar_Panel.objects.all()

        # Устанавливаем значение по умолчанию для ночного режима
        night_mode = request.COOKIES.get('night_mode', 'off')

        # Проверяем параметр 'night_mode' в GET запросе
        if 'night_mode' in request.GET:
            night_mode = request.GET['night_mode']

        # Обработка AJAX запросов
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            selected_panel_number = request.GET.get('selected_panel')
            if selected_panel_number == "all":
                characteristics = Characteristics.objects.all().order_by('-date', 'time')
            else:
                selected_panel = Solar_Panel.objects.get(installation_number=selected_panel_number)
                characteristics = Characteristics.objects.filter(solar_panel=selected_panel).order_by('-date', 'time')

            # Сериализуем queryset в JSON
            data = serializers.serialize('json', characteristics)
            response = JsonResponse({'data': data})
        else:
            # Создаем ответ для не-AJAX запросов
            response = render(request, 'dashboard.html', {'solar_panels': solar_panels, 'night_mode': night_mode})

        # Устанавливаем cookie в ответе
        response.set_cookie('night_mode', night_mode)
        return response
    



def get_characteristics_data(request, installation_number):
    characteristics = Characteristics.objects.filter(solar_panel__installation_number=installation_number).order_by('-date', 'time')
    data = {
        'labels': [f"{char.date} {char.time}" for char in characteristics],
        'generated_power_data': [char.generated_power for char in characteristics],
        # ... add other data as needed
    }
    return JsonResponse(data)


class CharTableView(View):
    def get(self, request, *args, **kwargs):
        night_mode = request.COOKIES.get('night_mode', 'off')

        # Проверяем параметр 'night_mode' в GET запросе
        if 'night_mode' in request.GET:
            night_mode = request.GET['night_mode']

        char = Characteristics.objects.order_by('-date', '-time') 
        
        response = render(request, "table.html", {'characteristics': char, 'night_mode': night_mode})
        response.set_cookie('night_mode', night_mode)

        return response


def solar_panels(request):
    night_mode = request.COOKIES.get('night_mode', 'off')

    solar = Solar_Panel.objects.all()
    return render(request, "panels.html", {'panels': solar, 'night_mode': night_mode})


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
    night_mode = request.COOKIES.get('night_mode', 'off')

    sol = Solar_Panel.objects.all()
    return render(request, "socket.html", {'night_mode': night_mode})


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