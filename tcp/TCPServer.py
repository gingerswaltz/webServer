import asyncio
import asyncpg
import json
from typing import Any, Tuple
import socket
import AbstractTCP
from typing import Any, Dict

class TCPServer(AbstractTCP.AbstractTCPServer):
    def __init__(self, host: str, port: int, database_config: Dict[str, Any]):
        super().__init__(host, port, database_config)
        self.server = None

    async def start_server(self) -> None:
        self.server = await asyncio.start_server(
            self.handle_client_wrapper, self.host, self.port
        )
        print(f"Server started on {self.host}:{self.port}")
        async with self.server:
            await self.server.serve_forever()

    async def handle_client_wrapper(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        address = writer.get_extra_info('peername')
        client_socket = writer.get_extra_info('socket')
        print(f"New client connected: {address}")
        
        # Создаем экземпляр TCPConnection
        connection = TCPConnection(self.database_config)
        
        # Обрабатываем клиентское подключение
        await connection.handle_client(client_socket, address)
        
        # Закрываем подключение
        writer.close()
        await writer.wait_closed()

    async def stop_server(self) -> None:
        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()
            print("Server has been stopped.")


class TCPConnection(AbstractTCP.AbstractTCPConnection):
    def __init__(self, database_config: dict):
        self.database_config = database_config

    async def handle_client(self, client_socket: socket.socket, address: Tuple[str, int]) -> None:
        try:
            # Получаем данные от клиента
            data = await self.receive_data(client_socket)
            # Вставляем данные в базу
            await self.insert_data(data)
            # Получаем обновленную запись (пример: получаем по ID)
            record = await self.fetch_record(data['id'])
            # Отправляем запись клиенту
            await self.send_record(client_socket, record)
        except Exception as e:
            self.log_exception(e)
        finally:
            await self.client_disconnect(client_socket, address)

    async def send_record(self, client_socket: socket.socket, data: Any) -> None:
        try:
            await client_socket.send(json.dumps(data).encode('utf-8'))
        except Exception as e:
            self.log_exception(e)

    async def receive_data(self, client_socket: socket.socket) -> Any:
        try:
            data = b''
            while True:
                chunk = await client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk
            return json.loads(data.decode('utf-8'))
        except Exception as e:
            self.log_exception(e)

    async def insert_data(self, data: Any) -> None:
        try:
            conn = await asyncpg.connect(**self.database_config)
            await conn.execute('INSERT INTO table_name (column1, column2) VALUES ($1, $2)',
                               data['column1'], data['column2'])
        except Exception as e:
            self.log_exception(e)
        finally:
            await conn.close()

    async def client_disconnect(self, client_socket: socket.socket, address) -> None:
        client_socket.close()
        return(f"Client {address[0]}:{address[1]} has disconnected.")

    async def fetch_record(self, record_id: int) -> Any:
        try:
            conn = await asyncpg.connect(**self.database_config)
            record = await conn.fetchrow('SELECT * FROM table_name WHERE id=$1', record_id)
            return record
        except Exception as e:
            self.log_exception(e)
        finally:
            await conn.close()

    def log_exception(self, exception: Exception) -> None:
        print(f"An exception occurred: {exception}")




# Пример использования TCPServer
if __name__ == "__main__":
    database_config = {
        # Предполагаемые параметры подключения к базе данных
        "user": "postgres",
        "password": "1",
        "database": "DBForWebServer",
        "host": "localhost"
    }

    server = TCPServer('127.0.0.1', 1024, database_config)
    asyncio.run(server.start_server())