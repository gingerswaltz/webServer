import socket

# Создание соксового сервера
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('85.193.80.133', 1024))  # Пример адреса и порта
server_socket.listen(1)  # Ожидание одного клиента

print("Ожидание подключения...")
client_socket, client_address = server_socket.accept()
print(f"Подключено к {client_address}")

try:
    while True:
        # Ввод с клавиатуры
        message = input("Введите сообщение для отправки клиенту (для завершения введите 'exit'): ")
        if message.lower() == 'exit':
            break

        # Отправка данных клиенту
        client_socket.sendall(message.encode())

except KeyboardInterrupt:
    print("Программа завершена пользователем.")
except Exception as e:
    print(f"Произошла ошибка: {e}")
finally:
    client_socket.close()
    server_socket.close()
