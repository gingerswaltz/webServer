import asyncio
import socket
import json
import psycopg2
import argparse

# Создание парсера аргументов
parser = argparse.ArgumentParser(description='Server Configuration')
parser.add_argument('--db-host', type=str, default='localhost', help='Database host')
parser.add_argument('--db-name', type=str, default='DBForWebServer', help='Database name')
parser.add_argument('--db-user', type=str, default='postgres', help='Database user')
parser.add_argument('--db-password', type=str, default='1', help='Database password')
parser.add_argument('--tcp-host', type=str, default='localhost', help='TCP server host')
parser.add_argument('--tcp-port', type=int, default=1024, help='TCP server port')
args = parser.parse_args()

# Использование аргументов в коде
db_host = args.db_host
db_name = args.db_name
db_user = args.db_user
db_password = args.db_password
tcp_host = args.tcp_host
tcp_port = args.tcp_port


# Время интервала опроса клиентов в секундах
polling_interval = 10

# Список подключенных клиентов
connected_clients = []

# Функция для добавления данных в базу данных
async def add_to_database(data):
    # Подключение к базе данных
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )
    cursor = conn.cursor()

    address_port = str(data['ip_address']) + str(data['port'])

    # Проверка наличия записи для указанной установки
    select_query = "SELECT COUNT(*) FROM main_reading WHERE installation_number = %s"
    cursor.execute(select_query, (data['installation_number'],))
    count = cursor.fetchone()[0]

    if count > 0:
        # Запись уже существует, выполнение операции обновления
        update_reading_query = "UPDATE main_reading SET date = %s, time = %s, generated_power = %s, consumed_power = %s, vertical_position = %s, horizontal_position = %s WHERE installation_number = %s"
        update_ip_query = "UPDATE main_ip SET ip_address = %s, port = %s WHERE reading_id = %s"
        
        cursor.execute(update_reading_query, (data['date'], data['time'], data['generated_power'], data['consumed_power'], data['vertical_position'], data['horizontal_position'], data['installation_number']))
        cursor.execute(update_ip_query, (data['ip_address'], data['port'], data['installation_number']))
    else:
        # Запись не существует, выполнение операции вставки
        insert_query = "INSERT INTO main_reading (installation_number, date, time, generated_power, consumed_power, vertical_position, horizontal_position) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        insert_ip_query = "INSERT INTO main_ip (ip_address, port,reading_id ) VALUES (%s, %s, %s)"
        
        cursor.execute(insert_query, (data['installation_number'], data['date'], data['time'], data['generated_power'], data['consumed_power'], data['vertical_position'], data['horizontal_position']))
        cursor.execute(insert_ip_query, (data['ip_address'], data['port'], data['installation_number']))
    
    conn.commit()
    cursor.close()
    conn.close()


# Функция для обработки подключения клиента
async def handle_client(client_socket, client_address):
    print(f"Установлено подключение с {client_address[0]}:{client_address[1]}")
    connected_clients.append((client_socket, client_address))

    while True:
        try:
            data = await loop.sock_recv(client_socket, 1024)

            # Проверка, является ли полученные данные пустыми. Если да, то клиент отключился.
            if not data:
                print(f"Подключение с {client_address[0]}:{client_address[1]} разорвано")
                connected_clients.remove((client_socket, client_address))
                break

            # Преобразование полученных данных из байтовой строки в строку в кодировке UTF-8.
            data = data.decode('utf-8')

            print("Получены данные:", data)

            # Добавление данных в базу данных.
            try:
                json_data = json.loads(data)
                await add_to_database(json_data)
                print("Данные успешно добавлены в базу данных")
            except (json.JSONDecodeError, psycopg2.Error) as e:
                print("Ошибка при обработке данных или добавлении в базу данных:", str(e))
        except (ConnectionResetError, ConnectionAbortedError):
            print(f"Подключение с {client_address[0]}:{client_address[1]} разорвано")
            connected_clients.remove((client_socket, client_address))
            break

# Функция для опроса клиентов
async def poll_clients():
    while True:
        await asyncio.sleep(polling_interval)
        print("Опрос клиентов...")
        disconnected_clients = []

        for client_socket, client_address in connected_clients:
            try:
                await loop.sock_sendall(client_socket, b"Ping")
                await loop.sock_recv(client_socket, 1024)
            except (ConnectionResetError, ConnectionAbortedError):
                print(f"Клиент {client_address[0]}:{client_address[1]} не отвечает, удаление из списка подключенных клиентов")
                disconnected_clients.append((client_socket, client_address))
            
            except Exception as e:
                print("Ошибка при работе:", str(e))

        for client_socket, client_address in disconnected_clients:
            connected_clients.remove((client_socket, client_address))

import threading

async def main():
    # Создание TCP-сокета
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((tcp_host, tcp_port))
    tcp_socket.listen(1)

    print(f"Ожидание TCP-подключения на {tcp_host}:{tcp_port}...")

    # Запуск задачи для обработки клиентов
    while True:
        client_socket, client_address = await loop.sock_accept(tcp_socket)
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

    # Запуск задачи для опроса клиентов
    threading.Thread(target=poll_clients).start()