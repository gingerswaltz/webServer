import asyncio
import logging
import threading
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
        result=server.send_message_debug()
        return web.Response(text="ok")
    except Exception as e:
        logging.error(f"Error sending message: {e}")
        return web.Response(status=500)



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
    server = TCPServer('127.0.0.1', 1024, database_config)
    loop = asyncio.new_event_loop()
    server_thread = threading.Thread(target=start_server_loop, args=(loop, server))
    server_thread.start()

    # Запуск HTTP сервера в том же цикле событий
    asyncio.run_coroutine_threadsafe(start_http_server(server), loop)

    # Дождаться завершения работы сервера
    server_thread.join()
