import socket
import json
from datetime import datetime
import random

def send_data_to_server(host, port, message):
    # Создаем соединение
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        # Отправляем начальное сообщение
        json_message = json.dumps(message) + '\n'
        print(f'Send: {json_message}')
        s.sendall(json_message.encode())

        while True:
            # Ввод команды пользователем
            print("Enter command (up, down, left, right, reset, shutdown, exit to stop): ")
            command = input()

            # Обработка команды shutdown и выхода
            if command.lower() in ["shutdown", "exit"]:
                break

            # Формирование и отправка сообщения
            response_message = {
                "header": "response",
                "command": command,
                "statement": str(bool(random.uniform(1, 0))),
                "solar_panel_id": installation_number,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            s.sendall(json.dumps(response_message).encode() + b'\n')
            print(f'Sent: {response_message}')

if __name__ == "__main__":
    server_host = '127.0.0.1'
    server_port = 1024

    print("Enter id: ")
    installation_number = input()

    try:
        installation_number = int(installation_number)
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M")
        generated_power = random.uniform(50, 150)
        consumed_power = random.uniform(50, 150)
        vertical_position = random.randint(1, 180)
        horizontal_position = random.randint(1, 180)
    except ValueError:
        print("Please enter a valid number for installation number.")
        exit(1)
    
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

    send_data_to_server(server_host, server_port, client_data)
