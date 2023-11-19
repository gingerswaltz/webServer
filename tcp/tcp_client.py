import asyncio
import json
from datetime import datetime
import random

async def tcp_client(host, port, message):
    try:
        reader, writer = await asyncio.open_connection(host, port)
        
        # Сериализуем сообщение в JSON и добавляем символ новой строки
        json_message = json.dumps(message) + '\n'
        print(f'Send: {json_message}')
        writer.write(json_message.encode())

        while True:
            # Чтение ответа от сервера
            data = await reader.read(4096)  # Буфер достаточного размера для чтения ответа
            if not data:
                print('The server closed the connection')
                break
            response = data.decode()
            print(f'Received: {response}')

            # Проверяем, содержит ли ответ сообщение о выключении сервера
            if "shutdown" in response:
                print("Received shutdown signal from server.")
                break

    except asyncio.CancelledError:
        # Задача была отменена, закрываем соединение
        print('Client is shutting down.')
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        print('Close the connection')
        writer.close()
        await writer.wait_closed()

async def main(server_host, server_port, client_data):
    # Запускаем клиент
    task = asyncio.create_task(tcp_client(server_host, server_port, client_data))
    
    try:
        # Ожидаем завершения задачи
        await task
    except KeyboardInterrupt:
        # Пользователь нажал Ctrl+C, отменяем задачу
        print('Caught keyboard interrupt, cancelling tasks...')
        task.cancel()
        await task

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
        "id": installation_number,
        "date": current_date,
        "time": current_time,
        "generated_power": generated_power,
        "consumed_power": consumed_power,
        "vertical_position": vertical_position,
        "horizontal_position": horizontal_position,
        "solar_panel_id": installation_number
    }

    asyncio.run(main(server_host, server_port, client_data))
