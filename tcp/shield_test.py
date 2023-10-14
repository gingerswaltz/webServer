import socket
import threading

# Создание соксового сервера
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('85.193.80.133', 1024))  # Пример адреса и порта
server_socket.listen(1)  # Ожидание одного клиента

print("Ожидание подключения...")
client_socket, client_address = server_socket.accept()
print(f"Подключено к {client_address}")

# Функция для отправки сообщений клиенту
def send_messages():
    while True:
        message = input("Введите сообщение для отправки клиенту (для завершения введите 'exit'): ")
        if message.lower() == 'exit':
            client_socket.sendall(b'exit')  # Отправляем 'exit' клиенту
            client_socket.close()  # Закрываем соединение с клиентом
            break
        client_socket.sendall(message.encode())

# Функция для приема сообщений от клиента
def receive_messages():
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        received_data = data.decode()
        if received_data.lower() == 'exit':
            client_socket.close()  # Закрываем соединение с клиентом
            break
        print(f"Получено от клиента: {received_data}")

# Создание и запуск потоков
send_thread = threading.Thread(target=send_messages)
receive_thread = threading.Thread(target=receive_messages)

send_thread.start()
receive_thread.start()

# Ожидание завершения работы потоков
send_thread.join()
receive_thread.join()

server_socket.close()
