import asyncio
import asyncpg
import json
from typing import Any, Tuple
import AbstractTCP
import logging
from typing import Any, Dict


class TCPServer(AbstractTCP.AbstractTCPServer):
    def __init__(self, host: str, port: int, database_config: Dict[str, Any]):
        super().__init__(host, port, database_config)
        self.server = None
        self.active_connections = {}  # Словарь активных подключений
        self.connection_id_mapping = {}  # Словарь для ID к writer
        self.next_client_id = 1  # Счетчик для следующего ID клиента
        self.current_connection_id = None  # Текущее активное подключение
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    async def start_server(self) -> None:
        self.server = await asyncio.start_server(
            self.handle_client_wrapper, self.host, self.port
        )
        logging.info(f"Server started on {self.host}:{self.port}")
        async with self.server:
            await self.server.serve_forever()

    def set_active_connection(self, client_id):
        """ Устанавливает активное подключение по ID. """
        writer = self.connection_id_mapping.get(int(client_id))
        if writer:
            self.current_connection_id = client_id
            logging.info(f"Active connection set to ID {client_id}")
        else:
            logging.error(f"Client ID {client_id} not found")

    def reset_current_connection(self):
        """ Сбрасывает текущее активное подключение. """
        self.current_connection_id = None

    
    async def send_message(self, message):
        """ Отправляет сообщение текущему активному клиенту. """
        writer = self.connection_id_mapping.get(self.current_connection_id)
        if writer:
            try:
                writer.write(json.dumps(message).encode('utf-8'))
                await writer.drain()
            except Exception as e:
                logging.error(f"Error sending message to client ID {self.current_connection_id}: {e}")
        else:
            logging.error(f"No active connection for client ID {self.current_connection_id}")


    async def handle_client_wrapper(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        client_id = self.next_client_id
        self.next_client_id += 1

        self.connection_id_mapping[client_id] = writer
        address = writer.get_extra_info('peername')
        logging.info(f"New client connected: {client_id} (Address: {address})")

        try:
            # Создаем экземпляр TCPConnection
            connection = TCPConnection(self.database_config)
            logging.info(connection)

            # Обрабатываем клиентское подключение, передавая экземпляр сервера
            await connection.handle_client(reader, writer, address, self)
        except Exception as e:
            logging.error(f"Error handling client {client_id}: {e}")
        finally:
            # Удаление клиента из словаря активных подключений при закрытии соединения
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            logging.info(f"Client {client_id} disconnected")
            writer.close()
            await writer.wait_closed()

    async def stop_server(self) -> None:
        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()
            logging.info("Server has been stopped.")


class TCPConnection(AbstractTCP.AbstractTCPConnection):
    def __init__(self, database_config: dict):
        """
        Инициализирует экземпляр TCPConnection с конфигурацией базы данных.

        Args:
            database_config (dict): Конфигурация подключения к базе данных.
        """
        self.database_config = database_config

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, address: Tuple[str, str], server: TCPServer) -> None:
        """
        Обрабатывает подключившегося клиента, читает данные, отправляет ответы и управляет подключениями.

        Этот метод регистрирует подключение в словаре активных подключений сервера, обрабатывает входящие данные от клиента,
        вставляет данные в базу данных и отправляет обратно соответствующие записи. Подключение удаляется из активных
        при его закрытии.

        Args:
            reader (asyncio.StreamReader): Объект StreamReader для чтения данных от клиента.
            writer (asyncio.StreamWriter): Объект StreamWriter для отправки данных клиенту.
            address (Tuple[str, str]): Адрес клиента в формате (IP, порт).
            server (TCPServer): Экземпляр сервера, управляющего активными подключениями.
        """
        client_id = f"{address[0]}:{
            address[1]}"  # Уникальный идентификатор клиента
        try:
            logging.info(f"Starting handle for {address}")
            # Регистрация подключения
            server.active_connections[client_id] = writer

            while not reader.at_eof():
                data = await self.receive_data(reader)
                if not data:
                    logging.info(f"No data received. Client {
                                 address} may have disconnected.")
                    break

                data['ip_address'] = address[0]
                data['port'] = str(address[1])
                logging.info(f"Data: {data}")

                await self.insert_data(data)
                record = await self.fetch_record(data['installation_number'])
                await self.send_record(client_id, record, server)

        except Exception as e:
            self.log_exception(e)
        finally:
            if client_id in server.active_connections:  # Удаление подключения при закрытии
                del server.active_connections[client_id]
            logging.info(f"Closing connection for {address}")
            writer.close()
            await writer.wait_closed()

    async def send_record(self, client_id: str, data: Any, server: TCPServer) -> None:
        """
        Отправляет данные указанному клиенту.

        Этот метод ищет StreamWriter для указанного клиента в словаре активных подключений сервера
        и отправляет ему данные в формате JSON. Если указанный клиент не найден, выдает ошибку.

        Args:
            client_id (str): Уникальный идентификатор клиента, которому нужно отправить данные.
            data (Any): Данные для отправки клиенту.
            server (TCPServer): Экземпляр сервера, содержащий информацию о всех активных подключениях.
        """
        writer = server.active_connections.get(client_id)
        if writer is None:
            logging.error(f"No active connection found for client {client_id}")
            return

        try:
            writer.write(json.dumps(data).encode('utf-8'))
            await writer.drain()
        except Exception as e:
            self.log_exception(e)

    async def receive_data(self, reader: asyncio.StreamReader) -> dict:
        try:
            raw_data = await reader.readuntil(b'\n')
            logging.info(f"Raw data: {raw_data!r}")  # Выведем сырые данные
            decoded_data = raw_data.decode('utf-8').strip()
            # Выведем декодированные данные
            logging.info(f"Decoded data: {decoded_data}")
            json_data = json.loads(decoded_data)
            logging.info(f"JSON data: {json_data}")  # Выведем JSON данные
            return json_data
        except asyncio.IncompleteReadError:
            logging.info("Client disconnected before sending a newline.")
            return {}
        except json.JSONDecodeError as e:
            self.log_exception(f"Received data is not valid JSON: {e}")
            return {}
        except Exception as e:
            self.log_exception(f"An exception occurred: {e}")
            return {}

    async def insert_data(self, data: Any) -> None:
        try:
            logging.info(f"Connecting to DB to insert data...")
            conn = await asyncpg.connect(**self.database_config)
            logging.info(f"Connected to DB. Inserting data...")
            await conn.execute('INSERT INTO main_solar_panel (installation_number, ip_address, port) VALUES ($1, $2, $3)',
                               data['installation_number'], data['ip_address'], data['port'])
            logging.info(f"Data inserted successfully.")
        except Exception as e:
            self.log_exception(e)
        finally:
            await conn.close()
            logging.info(f"DB connection closed.")

    async def client_disconnect(self, client_id: str, server: TCPServer) -> None:
        """
        Обрабатывает отключение клиента.

        Этот метод закрывает StreamWriter для указанного клиента и удаляет его из словаря
        активных подключений сервера. Если клиент уже был отключен или не найден, 
        записывает соответствующее сообщение в лог.

        Args:
            client_id (str): Уникальный идентификатор клиента, который необходимо отключить.
            server (TCPServer): Экземпляр сервера, содержащий информацию о всех активных подключениях.
        """
        writer = server.active_connections.get(client_id)
        if writer is None:
            logging.info(
                f"Client {client_id} already disconnected or not found.")
            return

        writer.close()
        await writer.wait_closed()
        logging.info(f"Client {client_id} has disconnected.")

        # Удаляем клиента из словаря активных подключений
        if client_id in server.active_connections:
            del server.active_connections[client_id]

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
        logging.exception(f"An exception occurred: {exception}")




