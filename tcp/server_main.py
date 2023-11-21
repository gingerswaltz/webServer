import asyncio
import threading
from TCPServer import TCPServer
import sys
#todo: не работает показ с

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
                for client_id in server.connection_id_mapping:
                    address = server.connection_id_mapping[client_id].get_extra_info('peername')
                    print(f"ID: {client_id}, Address: {address}")

            elif choice == '2':
                for client_id in server.connection_id_mapping:
                    address = server.connection_id_mapping[client_id].get_extra_info('peername')
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

    user_interface(server, loop)
