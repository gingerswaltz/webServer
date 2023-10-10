import socket

# Создание соксового сервера
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('185.108.197.41', 1024))  # Пример адреса и порта
server_socket.listen(5)

while True:
    print("Ожидание подключения...")
    client_socket, client_address = server_socket.accept()
    print(f"Подключено к {client_address}")

    # Получение локального IP-адреса и порта соксового соединения
    local_ip = client_socket.getsockname()[0]
    local_port = client_socket.getsockname()[1]
    
    print(f"Локальный IP-адрес: {local_ip}")
    print(f"Локальный порт: {local_port}")

    # Обработка данных с клиента и отправка ввода с клавиатуры клиенту
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        print(f"Получено от клиента: {data.decode()}")
        
        # Ввод с клавиатуры и отправка клиенту
        message = input("Введите сообщение для отправки клиенту: ")
        client_socket.sendall(message.encode())
    
    client_socket.close()