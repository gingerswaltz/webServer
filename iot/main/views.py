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
        solar_panels = Solar_Panel.objects.all().order_by('id')
        night_mode = request.COOKIES.get('night_mode', 'off')

        if 'night_mode' in request.GET:
            night_mode = request.GET['night_mode']

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Обработка AJAX запросов
            selected_panel_number = request.GET.get('selected_panel')
            if selected_panel_number == "all":
                characteristics = Characteristics.objects.all().order_by('-date', 'time')
            else:
                selected_panel = Solar_Panel.objects.get(installation_number=selected_panel_number)
                characteristics = Characteristics.objects.filter(solar_panel=selected_panel).order_by('-date', 'time')

            # Сериализация данных для AJAX запросов
            data = serializers.serialize('json', characteristics)
            return JsonResponse({'data': data})
        else:
    
            # Формирование контекста для шаблона
            context = {
                'solar_panels': solar_panels,
                'night_mode': night_mode,
                
            }

            # Создание HTTP ответа
            response = render(request, 'dashboard.html', context)
            response.set_cookie('night_mode', night_mode)
            return response
    

def get_characteristics_data_by_panel(request, panel_id):
    # Получение данных по конкретной солнечной установке
    characteristics = Characteristics.objects.filter(solar_panel_id=panel_id)

    # Подготовка данных для графика
    generated_power = [c.generated_power for c in characteristics]
    consumed_power = [c.consumed_power for c in characteristics]

    # Сериализация данных в JSON
    data = {
        'generated_power': generated_power,
        'consumed_power': consumed_power
    }
    return JsonResponse(data)


def get_general_characteristics_data(request):
    # Получение всех записей из модели
    characteristics = Characteristics.objects.all().order_by('-date', 'time')
    generated_power = [c.generated_power for c in characteristics]
    consumed_power = [c.consumed_power for c in characteristics]

    # Сериализация данных в JSON для графика
    data = {
        'generated_power': generated_power,
        'consumed_power': consumed_power
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