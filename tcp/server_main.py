import asyncio
import threading
from TCPServer import TCPServer
<<<<<<< HEAD
import sys
=======
from aiohttp import web
import json

# Функция для запуска HTTP-сервера
async def start_http_server(server):
    app = web.Application()
    app.add_routes([
        web.get('/clients', lambda request: handle_clients(request, server)),
        web.post('/set_active_client', lambda request: handle_set_active_client(request, server)),
        web.post('/send_message', lambda request: handle_send_message(request, server)),
        web.post('/stop_server', lambda request: handle_stop_server(request, server))
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 8080)
    await site.start()

# Обработчики запросов
async def handle_clients(request, server):
    client_list = {client_id: server.connections_mapping[client_id].writer.get_extra_info('peername') for client_id in server.connections_mapping}
    return web.Response(text=json.dumps(client_list))

async def handle_set_active_client(request, server):
    data = await request.json()
    client_id = data.get('client_id')
    server.set_active_connection(client_id)
    return web.Response(text=f"Активный клиент установлен: {client_id}")

async def handle_send_message(request, server):
    data = await request.json()
    message = data.get('message')
    await server.send_message(message)
    return web.Response(text="Сообщение отправлено")

async def handle_stop_server(request, server):
    await server.stop_server()
    return web.Response(text="Сервер остановлен")

>>>>>>> parent of cd0828a (HTTP интеграция произведена успешно.)

def start_server_loop(loop, server):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(server.start_server())

def user_interface(server, loop):
    while True:
        try:
            print("\nДоступные команды:")
            print("1: Показать список подключенных клиентов")
            print("2: Выбрать клиента для отправки сообщения")
            print("3: Отправить сообщение выбранному клиенту")
            print("4: Остановить сервер и выйти")
            choice = input("Введите команду: ")

            if choice == '1':
                for client_id in server.connections_mapping:
                    address = server.connections_mapping[client_id].writer.get_extra_info('peername')
                    print(f"ID: {client_id}, Address: {address}")


            elif choice == '2':
                for client_id in server.connections_mapping:
                    address = server.connections_mapping[client_id].writer.get_extra_info('peername')
                    print(f"ID: {client_id}, Address: {address}")
                client_id = input("Введите ID клиента: ")
                try:
                    server.set_active_connection(int(client_id))
                except ValueError:
                    print("Ошибка: Введите корректный числовой ID клиента.")

            elif choice == '3':
                message = input("Введите сообщение: ")
                asyncio.run_coroutine_threadsafe(server.send_message(message), loop)

            elif choice == '4':
                asyncio.run_coroutine_threadsafe(server.stop_server(), loop).result()
                break

        except Exception as e:
            print(f"Произошла ошибка: {e}")

    sys.exit(0)

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
<<<<<<< HEAD

    user_interface(server, loop)
=======
    # Запуск HTTP сервера в том же цикле событий
    asyncio.run_coroutine_threadsafe(start_http_server(server), loop)
>>>>>>> parent of cd0828a (HTTP интеграция произведена успешно.)
