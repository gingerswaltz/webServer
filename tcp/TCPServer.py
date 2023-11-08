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
        print(f"New client connected: {address}")
    
    # Создаем экземпляр TCPConnection
        connection = TCPConnection(self.database_config)
        print(connection)
    # Обрабатываем клиентское подключение
        await connection.handle_client(reader, writer, address)
    
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

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, address: Tuple[str, str]) -> None:
        try:
            print(f"Starting handle for {address}")
            while not reader.at_eof():
                # Получаем данные от клиента
                data = await self.receive_data(reader)
                if not data:  # Если данных нет, возможно клиент отключился
                    print(f"No data received. Client {address} may have disconnected.")
                    break

                print("Received data:", data)
                if not isinstance(data, dict):
                    raise ValueError("Data received is not a dictionary")

                # Добавляем IP-адрес и порт клиента к данным
                data['ip_address'] = address[0]
                data['port'] = str(address[1])
                print(f"Data: {data}")

                # Вставляем данные в базу и отправляем обратно, если это необходимо
                await self.insert_data(data)
                record = await self.fetch_record(data['installation_number'])
                await self.send_record(writer, record)

        except Exception as e:
            self.log_exception(e)
        finally:
            # Теперь закрытие соединения произойдет здесь, если цикл прерван или произошла ошибка
            print(f"Closing connection for {address}")
            writer.close()
            await writer.wait_closed()

    async def send_record(self, writer: asyncio.StreamWriter, data: Any) -> None:
        try:
            writer.write(json.dumps(data).encode('utf-8'))
            await writer.drain()  # Убедитесь, что все данные отправлены
        except Exception as e:
            self.log_exception(e)


    async def receive_data(self, reader: asyncio.StreamReader) -> dict:
        try:
            raw_data = await reader.readuntil(b'\n')
            print(f"Raw data: {raw_data!r}")  # Выведем сырые данные
            decoded_data = raw_data.decode('utf-8').strip()
            print(f"Decoded data: {decoded_data}")  # Выведем декодированные данные
            json_data = json.loads(decoded_data)
            print(f"JSON data: {json_data}")  # Выведем JSON данные
            return json_data
        except asyncio.IncompleteReadError:
            print("Client disconnected before sending a newline.")
            return {}
        except json.JSONDecodeError as e:
            self.log_exception(f"Received data is not valid JSON: {e}")
            return {}
        except Exception as e:
            self.log_exception(f"An exception occurred: {e}")
            return {}





    async def insert_data(self, data: Any) -> None:
        try:
            print(f"Connecting to DB to insert data...")
            conn = await asyncpg.connect(**self.database_config)
            print(f"Connected to DB. Inserting data...")
            await conn.execute('INSERT INTO main_solar_panel (installation_number, ip_address, port) VALUES ($1, $2, $3)',
                               data['installation_number'], data['ip_address'], data['port'])
            print(f"Data inserted successfully.")
        except Exception as e:
            self.log_exception(e)
        finally:
            await conn.close()
            print(f"DB connection closed.")

    async def client_disconnect(self, writer: asyncio.StreamWriter, address) -> None:
        writer.close()
        await writer.wait_closed()
        print(f"Client {address[0]}:{address[1]} has disconnected.")


    async def fetch_record(self, record_id: int) -> dict:
        try:
            conn = await asyncpg.connect(**self.database_config)
            record = await conn.fetchrow(
            'SELECT * FROM main_solar_panel WHERE installation_number = $1',
            record_id
        )
            # Конвертируем Record в словарь перед возвращением
            return dict(record) if record else {}
        except Exception as e:
            self.log_exception(e)
            return {}


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