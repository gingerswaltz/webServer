import socket
import json
from datetime import datetime
import random


def send_data_to_server(host, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        # Отправляем начальное сообщение
        json_message = json.dumps(message) + '\n'
        print(f'Send: {json_message}')
        s.sendall(json_message.encode())

        try:
            while True:
                # Ожидаем команды от сервера
                data = s.recv(4096)
                if not data:
                    break  # Если нет данных, заканчиваем цикл

                command = data.decode()  # Декодируем команду из байтов в строку

                # Обработка полученной команды
                print(f'Received command: {command}')
                if command == "shutdown":
                    break

                # Формирование и отправка ответа
                response_message = {
                    "header": "response",
                    "command": command,
                    "statement": str(bool(round(random.uniform(0, 1)))),
                    "solar_panel_id": installation_number,
                    "date": datetime.now().strftime("%Y-%m-%d")+datetime.now().strftime("%H:%M")
                }
                s.sendall(json.dumps(response_message).encode() + b'\n')
                print(f'Sent: {response_message}')
        except json.JSONDecodeError as e:
            print("Error decoding JSON data from server:", e)
        finally:
            s.close()
            
if __name__ == "__main__":
    # server_host = '85.193.80.133'
    server_host = 'localhost'
    server_port = 1024
    print("Enter id: ")
    installation_number = input()
    running = True  # Флаг для управления выполнением цикла
    try:
        installation_number = int(installation_number)
    except ValueError:
        print("Please enter a valid number for installation number.")
        exit(1)

    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")
    generated_power = random.uniform(50, 150)
    consumed_power = random.uniform(50, 100)
    vertical_position = random.randint(1, 180)
    horizontal_position = random.randint(1, 180)

    client_data = {
        "header": "update",
        "id": installation_number,
        "date": current_date,
        "time": current_time,
        "generated_power": generated_power,
        "consumed_power": consumed_power,
        "vertical_position": vertical_position,
        "horizontal_position": horizontal_position,
        "solar_panel_id": installation_number
    }

    while running:
        try:
            send_data_to_server(server_host, server_port, client_data)
        except KeyboardInterrupt as e:
            print("\nCtrl+C detected. Exiting gracefully.")
            running=False
