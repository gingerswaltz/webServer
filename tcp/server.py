import argparse
import psycopg2
import socket
import json
import threading

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
polling_interval = 30

# Список подключенных клиентов
connected_clients = []
# Создание мьютекса для доступа к connected_clients
connected_clients_mutex = threading.Lock()

def add_to_database(data):
    # Подключение к базе данных
        conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
        )
        cursor = conn.cursor()


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




def handle_client(client_socket, client_address):
    print(f"Установлено подключение с {client_address[0]}:{client_address[1]}")
    
    try:
        data = client_socket.recv(1024)      
    except Exception as e:
        print(e)
    else:
        data = data.decode('utf-8')  # Преобразование байтов в строку UTF-8

        # Получите IP-адрес и порт клиента
        client_ip, client_port = client_address
        
        # Обновите JSON-структуру
        try:
            json_data = json.loads(data)
            json_data["ip_address"] = client_ip
            json_data["port"] = client_port
            
            # Добавление данных в базу данных.
            add_to_database(json_data)
            print("Данные успешно добавлены в базу данных")
        except (json.JSONDecodeError, psycopg2.Error) as e:
            print("Ошибка при обработке данных или добавлении в базу данных:", str(e))

            
def main():
    # Создание TCP-сокета
    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.bind((tcp_host, tcp_port))
        tcp_socket.listen()
          
        print(f"Ожидание TCP-подключения на {tcp_host}:{tcp_port}...")
    
        # poll_thread = threading.Thread(target=poll_clients, args=())
        # poll_thread.start()
    
        while True:
            client_socket, client_address = tcp_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            connected_clients.append((client_socket, client_address))
            #print(f"Клиент {client_address[0]}:{client_address[1]} добавлен в список")
            client_thread.start()

    except Exception as e:
                    print("Ошибка при работе main:", str(e))



if __name__ == "__main__":
    main()


      