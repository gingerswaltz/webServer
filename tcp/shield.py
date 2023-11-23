import socket
import threading
import time

# Создание соксового сервера
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('85.193.80.133', 1024))  # Пример адреса и порта
server_socket.listen(1)  # Ожидание одного клиента
client_socket = None

print("Ожидание подключения...")
client_socket, client_address = server_socket.accept()
print(f"Подключено к {client_address}")

# Функция для отправки сообщений клиенту
def send_messages():
    while True:
        message = input("Введите сообщение для отправки клиенту (для завершения введите 'exit'): ")
        if message.lower() == 'exit':
            client_socket.sendall(message.encode())  # Отправляем 'exit' клиенту
            break
        client_socket.sendall(message.encode())

# Функция для отправки сообщения клиенту каждую минуту
def send_periodic_message():
    global client_socket
    while True:
        time.sleep(60)  # Ждем 60 секунд
        message = "awake from sleep"
        client_socket.sendall(message.encode())

# Функция для приема сообщений от клиента
def receive_messages():
    while True:
        data = client_socket.recv(1024)
        if not data:
            print("Закрытие соединения")
            break
        received_data = data.decode()
        if received_data.lower() == 'exit':
            client_socket.close()  # Закрываем соединение с клиентом
            break
        print(f"Получено от клиента: {received_data}")

def main():
    global client_socket
    while True:
        print("Ждем подключения клиента...")
        client_socket, client_address = server_socket.accept()
        print(f"Подключен клиент: {client_address}")
        send_thread = threading.Thread(target=send_messages)
        receive_thread = threading.Thread(target=receive_messages)
        periodic_message_thread = threading.Thread(target=send_periodic_message)
        send_thread.start()
        receive_thread.start()
        periodic_message_thread.start()
        send_thread.join()
        receive_thread.join()
        periodic_message_thread.join()


# Запускаем главную функцию
if __name__ == "__main__":
    main()
