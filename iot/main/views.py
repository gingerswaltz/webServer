import time
from django.views.generic import View
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from .models import Solar_Panel, Characteristics
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import requests
import json
from django.template.defaultfilters import date
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

SERVER_URL = 'http://127.0.0.1:8080'  # адрес интерфейса TCP сервера

# Класс представления Dashboard
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
                selected_panel = Solar_Panel.objects.get(
                    installation_number=selected_panel_number)
                characteristics = Characteristics.objects.filter(
                    solar_panel=selected_panel).order_by('-date', 'time')

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

# # Получение данных по конкретной солнечной установке
def get_characteristics_data_by_panel(request, panel_id):
    # фильтруем по переданному panel id.
    characteristics = Characteristics.objects.filter(solar_panel_id=panel_id)

    # Подготовка данных для графика
    generated_power = [c.generated_power for c in characteristics]
    consumed_power = [c.consumed_power for c in characteristics]
    date = [c.date for c in reversed(characteristics)]

    # Сериализация данных в JSON
    data = {
        'generated_power': generated_power,
        'consumed_power': consumed_power,
        'date': date,
    }
    return JsonResponse(data)


def get_general_characteristics_data(request):
    # Получение всех записей из модели
    characteristics = Characteristics.objects.all().order_by('-date', 'time')
    generated_power = [c.generated_power for c in characteristics]
    consumed_power = [c.consumed_power for c in characteristics]
    date = [c.date for c in reversed(characteristics)]

    # Сериализация данных в JSON для графика
    data = {
        'generated_power': generated_power,
        'consumed_power': consumed_power,
        'date': date,
    }
    return JsonResponse(data)

# Класс представления table.html
class CharTableView(View):
    def get(self, request, *args, **kwargs):
        night_mode = request.COOKIES.get('night_mode', 'off')

        # Проверяем параметр 'night_mode' в GET запросе
        if 'night_mode' in request.GET:
            night_mode = request.GET['night_mode']

        char = Characteristics.objects.order_by('-date', '-time')
        solar_panels = Solar_Panel.objects.all().order_by('id')
        response = render(request, "table.html", {
                          'characteristics': char, 'night_mode': night_mode, "solar_panels": solar_panels,
                          })
        response.set_cookie('night_mode', night_mode)

        return response

# panels.html
def solar_panels(request):
    night_mode = request.COOKIES.get('night_mode', 'off')
    connected_clients = get_connected_clients(request)
    # Декодирование содержимого JsonResponse и преобразование в Python-словарь
    connected_clients_content = connected_clients.content.decode(
        'utf-8')  # Получить содержимое как строку
    # Преобразовать строку JSON в словарь
    connected_clients_data = json.loads(connected_clients_content)

    # Извлечение ключей из словаря
    connected_clients = list(connected_clients_data.keys())
    print(connected_clients)
    solar = Solar_Panel.objects.all().order_by('id')
    return render(request, "panels.html", {'panels': solar, 'night_mode': night_mode, 'connected_clients': connected_clients})

# ??? TODO DOC (ALEXEY)
def characteristics_data(request):
    # Get the selected solar panel if provided
    selected_panel_id = request.GET.get('solar_panel')
    if selected_panel_id:
        characteristics = Characteristics.objects.filter(
            solar_panel_id=selected_panel_id)
    else:
        characteristics = Characteristics.objects.all()

    # Prepare the data for the response
    data = {
        'dates': [char.date.strftime("%Y-%m-%d") for char in characteristics],
        'generated_power': [char.generated_power for char in characteristics],
        'consumed_power': [char.consumed_power for char in characteristics],
    }

    return JsonResponse(data)

# устарело: представление socket.html
def socket(request):
    night_mode = request.COOKIES.get('night_mode', 'off')

    sol = Solar_Panel.objects.all()
    return render(request, "socket.html", {'night_mode': night_mode})


# Самая последняя запись характеристик панели (JSON)
def get_recent_char(request, panel_id):
    try:
        characteristics = Characteristics.objects.filter(
            solar_panel_id=panel_id).latest('date', 'time')
        # Формируем данные для JSON-ответа
        data = {
            'horizontal_position': f"{characteristics.horizontal_position}°",
            'vertical_position': f"{characteristics.vertical_position}°",
            'consumed_power': f"{characteristics.consumed_power:.2f}",
            'generated_power': f"{characteristics.generated_power:.2f} w",
            'date': date(characteristics.date, "DATE_FORMAT"),
            'time': characteristics.time.strftime("%H:%M"),
        }

        return JsonResponse(data)
    except Characteristics.DoesNotExist:
        return JsonResponse({'error': 'Characteristics not found'}, status=404)

# panel_detail.html
def panel_detail(request):
    night_mode = request.COOKIES.get('night_mode', 'off')
    # Извлечение ID панели из GET-запроса
    panel_id = request.GET.get('id')
    characteristics = Characteristics.objects.filter(
        solar_panel_id=panel_id).latest('date', 'time')

    # Получение объекта панели из базы данных или возврат 404, если такой панель не найдена
    panel = get_object_or_404(Solar_Panel, id=panel_id)

    context = {
        'panel': panel,
        'night_mode': night_mode,
        'char': characteristics,
    }

    return render(request, "panel_detail.html", context)

# получение погоды (OpenWeatherAPI)
def get_weather(request, city="Chita"):
    try:
        api_key = 'f8e3947fda7d5cb9ce646407ff31d731'  # ключ для доступа
        base_url = 'http://api.openweathermap.org/data/2.5/weather'  # базовая ссылка к api

        # доп. параметры добавляемые к базовой ссылке
        params = {
            'q': city,  # город по умолчанию Чита
            'appid': api_key,  # ключ доступа
            'units': 'metric',  # Для получения погоды в метрической системе
            'lang': 'ru',  # Добавляем параметр lang для получения данных на русском
        }

        response = requests.get(base_url, params=params)  # запрос к api погоды
        response.raise_for_status()  # Генерирует исключение, если ответ содержит ошибку

        weather_data = response.json()  # парсим погоду с запроса к api
        # получаем направление ветра, преобразуем его из градусного в обычный вид
        wind = wind_direction(weather_data['wind']['deg'])
        # на интерфейс передаем обычный вид направления ветра
        weather_data['wind']['deg'] = wind
        return JsonResponse(weather_data)
    except requests.exceptions.RequestException as e:
        # Обработка исключений, связанных с запросом к API OpenWeatherMap
        print(f"Ошибка при запросе к OpenWeatherMap: {e}")
        return JsonResponse({'error': f"Ошибка при запросе к OpenWeatherMap: {e}"}, status=500)
    except KeyError as e:
        # Обработка исключений, связанных с отсутствием ожидаемых ключей в ответе API
        print(f"Ошибка при обработке ответа OpenWeatherMap: {e}")
        return JsonResponse({'error': f"Ошибка при обработке ответа OpenWeatherMap: {e}"}, status=500)
    except Exception as e:
        # Обработка других неожиданных исключений
        print(f"Необработанная ошибка: {e}")
        return JsonResponse({'error': f"Необработанная ошибка: {e}"}, status=500)


# направление ветра согласно полученным градусам с openweatherapi
def wind_direction(degrees):
    if degrees >= 337.5 or degrees < 22.5:
        return 'Северный'
    elif 22.5 <= degrees < 67.5:
        return 'Северо-восточный'
    elif 67.5 <= degrees < 112.5:
        return 'Восточный'
    elif 112.5 <= degrees < 157.5:
        return 'Юго-восточный'
    elif 157.5 <= degrees < 202.5:
        return 'Южный'
    elif 202.5 <= degrees < 247.5:
        return 'Юго-западный'
    elif 247.5 <= degrees < 292.5:
        return 'Западный'
    elif 292.5 <= degrees < 337.5:
        return 'Северо-западный'
    else:
        return 'Неизвестное направление'


### функции TCP сервера

# получить список клиентов и их новые данные (ip, port)
def get_connected_clients(request):
    try:
        response = requests.get(f"{SERVER_URL}/clients")
        if response.ok:
            print(response.json())
            return JsonResponse(response.json())
        else:
            return JsonResponse({"error": "Ошибка при получении списка клиентов"}, status=500)
    except Exception as e:
        return JsonResponse({"error": "Ошибка при получении списка клиентов"}, status=500)

# Ставим активного клиента (которому сообщение отправляем)
def set_active_client(request):
    client_id = request.POST.get('client_id')
    response = requests.post(
        f"{SERVER_URL}/set_active_client", json={"client_id": client_id})
    if response.ok:
        return JsonResponse({"message": "Активный клиент установлен"})
    else:
        return JsonResponse({"error": "Ошибка при установке активного клиента"}, status=500)

# Отправка сообщения
def send_message_to_client(request):
    message = request.POST.get('message')
    response = requests.post(
        f"{SERVER_URL}/send_message", json={"message": message})
    if response.ok:
        return JsonResponse({"message": "Сообщение отправлено"})
    else:
        return JsonResponse({"error": "Ошибка при отправке сообщения"}, status=500)


# Метод, выполняемый при получении сигнала о подключении/отключении клиента, передаёт информацию в представление websocket
@csrf_exempt
def update_client_status(request):

    # Задержка выполнения представления на 0.5 секунд, чтобы успели данные по установке обновиться
    time.sleep(0.5)
    if request.method == 'POST':
        try:
            # JSON структура
            data = json.loads(request.body)
            # Получение нового порта и ip адреса
            sol = Solar_Panel.objects.get(id=data['client_id'])
            data['port'] = sol.port
            data['address'] = sol.ip_address

            # Получить слой каналов
            channel_layer = get_channel_layer()

            # Асинхронно отправить сообщение в группу
            async_to_sync(channel_layer.group_send)(
                "client_status_group",
                {
                    "type": "send.client.status",  # Соответствует методу в Consumer
                    "data": data  # Данные, которые вы хотите отправить
                }
            )

            return JsonResponse({"message": "Data received and processed successfully"})
        except json.JSONDecodeError as e:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
