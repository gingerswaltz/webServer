import asyncio
import json
from datetime import datetime
import random

async def send_data_to_server(host, port, message):
    reader, writer = await asyncio.open_connection(host, port)
    
    # Отправляем начальное сообщение
    json_message = json.dumps(message) + '\n'
    print(f'Send: {json_message}')
    writer.write(json_message.encode())

    while True:
        # Чтение ответа от сервера
        data = await reader.read(4096)
        if not data:
            print('The server closed the connection')
            break
        response = data.decode()
        print(f'Received: {response}')

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
            "statement": "User command",
            "solar_id_id": installation_number,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        writer.write(json.dumps(response_message).encode() + b'\n')
        await writer.drain()
        print(f'Sent: {response_message}')

    writer.close()
    await writer.wait_closed()

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

    asyncio.run(send_data_to_server(server_host, server_port, client_data))
