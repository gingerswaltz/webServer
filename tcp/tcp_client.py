import asyncio
import json

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
            print(f'Received: {data.decode()}')

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
        # Ожидаем завершения задачи (которое никогда не произойдет, пока не будет нажат Ctrl+C)
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
    except ValueError:
        print("Please enter a valid number for installation number.")
        exit(1)

    client_data = {
        "installation_number": installation_number
    }

    # Запускаем бесконечный цикл клиента до прерывания (Ctrl+C)
    asyncio.run(main(server_host, server_port, client_data))
