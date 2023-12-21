import asyncio
import logging
import threading

import aiohttp
from TCPServer import TCPServer
from aiohttp import web
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Функция для запуска HTTP-сервера
async def start_http_server(server):
    app = web.Application()
    app.add_routes([
        web.get('/clients', lambda request: handle_clients(request, server)),
        web.post('/set_active_client', lambda request: handle_set_active_client(request, server)),
        web.post('/send_message', lambda request: handle_send_message(request, server)),
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 8080)
    await site.start()

# Обработчики запросов
async def handle_clients(request, server):
    try:
        client_list = {client_id: server.connections_mapping[client_id].writer.get_extra_info('peername') for client_id in server.connections_mapping}
        return web.Response(text=json.dumps(client_list))
    except Exception as e:
        logging.error(f"Error handling clients request: {e}")
        return web.Response(status=500)

async def handle_set_active_client(request, server):
    try:
        data = await request.json()
        client_id = data.get('client_id')
        server.set_active_connection(int(client_id))
        if (server.current_connection_id==int(client_id)):
            return web.Response(text=f"Активный клиент установлен: {client_id}")
        else:
            return web.Response(status=500)
    except Exception as e:
        logging.error(f"Error setting active client: {e}")
        return web.Response(status=500)

async def handle_send_message(request, server):
    try:
        data = await request.json()
        message = data.get('message')
        await server.send_message(message)
        return web.Response(text="Сообщение отправлено")
    except Exception as e:
        logging.error(f"Error sending message: {e}")
        return web.Response(status=500)

# Callback для уведомления об отключении
async def notify_client_disconnection(client_id):
    try:
        # Подготовка данных для отправки
        data_to_send = json.dumps({"header": 'disconnect',"client_id": client_id})

        # Отправка данных
        async with aiohttp.ClientSession() as session:
            async with session.post('http://127.0.0.1:8000/update_client_status/', data=data_to_send) as response:
                if response.status == 200:
                    logging.info(f"Successfully notified disconnection of client {client_id}")
                else:
                    logging.error(f"Failed to notify disconnection of client {client_id}: {response.status}")
    except Exception as e:
        logging.error(f"Error notifying disconnection of client {client_id}: {e}")

# Callback для уведомления о подключении
async def notify_client_connection(client_id):
    try:
        # Подготовка данных для отправки
        data_to_send = json.dumps({"header": 'connect',"client_id": client_id})

        # Отправка данных
        async with aiohttp.ClientSession() as session:
            async with session.post('http://127.0.0.1:8000/update_client_status/', data=data_to_send) as response:
                if response.status == 200:
                    logging.info(f"Successfully notified new connection of client {client_id}")
                else:
                    logging.error(f"Failed to notify new connection of client {client_id}: {response.status}")
    except Exception as e:
        logging.error(f"Error notifying new connection of client {client_id}: {e}")


def start_server_loop(loop, server):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(server.start_server())

if __name__ == "__main__":
    database_config = {
        "user": "postgres",
        "password": "1",
        "database": "DBForWebServer",
        "host": "localhost"
    }
    server = TCPServer('127.0.0.1', 1024, database_config, disconnection_callback=notify_client_disconnection, connection_callback=notify_client_connection)
    loop = asyncio.new_event_loop()
    server_thread = threading.Thread(target=start_server_loop, args=(loop, server))
    server_thread.start()

    # Запуск HTTP сервера в том же цикле событий
    asyncio.run_coroutine_threadsafe(start_http_server(server), loop)

    # Дождаться завершения работы сервера
    server_thread.join()
