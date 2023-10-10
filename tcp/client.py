import socket
import json
import argparse
import time
print("Run with --tcp-host ip  or  --tcp-port port, where ip  and port is that is u need. default is localhost:1024")

# Настройки TCP-сервера
parser = argparse.ArgumentParser(description='Server Configuration')
parser.add_argument('--tcp-host', type=str, default='127.0.0.1', help='Tcp host')
parser.add_argument('--tcp-port', type=str, default='1024', help='Tcp port')
args = parser.parse_args()




tcp_host = args.tcp_host
tcp_port = args.tcp_port

# Данные для отправки
data = {}

data['installation_number']=input('Номер установки: ')
data['date']=input('Дата (дд.мм.гг): ') or '20.03.2020'
data['time']=input('Время (чч:мм): ') or '15:30'
data['generated_power']=input('Сгенерированная мощ-ть: ') or '300'
data['consumed_power']=input('Потребленная мощ-ть: ') or '400'
data['vertical_position']=input('Вертикальный угол: ') or '500'
data['horizontal_position']=input('Горизонтальный угол: ') or '600'


# Преобразование данных в JSON-строку

while True:
    try:
        # Создание TCP-сокета
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Подключение к серверу
        tcp_socket.connect((tcp_host, int(tcp_port)))
        socket_address = tcp_socket.getsockname()
        address = socket_address[0]
        port = socket_address[1]

        print(f'Успешное подключение к серверу {tcp_host}:{tcp_port}')

        json_data = json.dumps(data)

        # Отправка данных
        tcp_socket.sendall(json_data.encode('utf-8'))
        print(f'Данные отправлены: {json_data}')

        # Получение ответа от сервера
        response = tcp_socket.recv(1024)
        print('Получен ответ от сервера:', response.decode('utf-8'))

        # Закрытие соединения
        tcp_socket.close()

        # Ожидание 2 минут перед следующей отправкой
        time.sleep(120)
    except Exception as e:
        print('Ошибка при отправке данных:', str(e))