from AbstractTCP import TCPServer
import socket
import asyncio
import json


# Класс TCP сервера
class MyTCPServer(TCPServer):
    def __init__(self, host, port, database_connection):
        super().__init__(host, port)
        self.database_connection=database_connection

    async def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(50)  # Максимальное количество ожидающих соединений

            #print(f"Сервер запущен на {self.host}:{self.port}")

            while True:
                client_socket, client_address = self.server_socket.accept()
               # print(f"Подключение от {client_address}")
                asyncio.create_task(self.handle_client(client_socket))
        except Exception as e:
            return str(e)

    async def handle_client(self, client_socket):
        try:
            data=await self.receive_data(client_socket)
            request=json.loads(data)
        # Запись данных в базу данных PostgreSQL
            self.insert_data_into_database(request)
        #todo: logic process
        except Exception as e:
            return str(e)
    
    
    async def receive_data(self, client_socket):
        try:
            data=b""
            while True:
                chunk=await client_socket.recv(1024)
                if not chunk:
                    break
                data+=chunk
            return data.decode("utf-8")
        except Exception as e:
            return str(e)
    
    
    def insert_data_into_database(self, data):
        try:
            conn = psycopg2.connect(**self.database_connection)
            cursor = conn.cursor()

            # Пример SQL-запроса для вставки данных в таблицу
            sql = "INSERT INTO table_name (column1, column2) VALUES (%s, %s)"
            values = (data["value1"], data["value2"])  # Заменить на реальные значения

            cursor.execute(sql, values)
            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            return str(e)

    def stop(self):
        # Здесь вы можете реализовать логику остановки сервера
        pass

   

    def fetch_updated_record(self):
        # Здесь вы можете реализовать извлечение измененной записи из базы данных
        pass

    def send_record_to_client(self, client_socket, record):
        # Здесь вы можете реализовать отправку записи клиенту по TCP-соксету
        pass
