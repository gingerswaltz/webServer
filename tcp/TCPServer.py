import asyncio
import asyncpg
import json
from typing import Any, Tuple
import AbstractTCP
import logging
from typing import Any, Dict

#todo stop_server, отправка данных


# Класс TCP Сервера
class TCPServer(AbstractTCP.AbstractTCPServer):
    def __init__(self, host: str, port: int, database_config: Dict[str, Any]):
        super().__init__(host, port, database_config)
        self.server = None
        self.active_connections = {}  # Словарь активных подключений
        self.connection_id_mapping = {}  # Словарь для ID к writer
        self.next_client_id = 1  # Счетчик для следующего ID клиента
        self.current_connection_id = None  # Текущее активное подключение
        self.running = False  # Флаг состояния работы
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    async def start_server(self):
        self.server = await asyncio.start_server(self.handle_client_wrapper, self.host, self.port)
        logging.info(f"Server started on {self.host}:{self.port}")
        self.running = True
        while self.running:
            await asyncio.sleep(1)  # Таймаут проверки состояния
        logging.info("Server has been stopped.")

    # Выбор активного подключения
    def set_active_connection(self, client_id):
        """ Устанавливает активное подключение по ID. """
        writer = self.connection_id_mapping.get(int(client_id))
        if writer:
            self.current_connection_id = client_id
            logging.info(f"Active connection set to ID {client_id}")
        else:
            logging.error(f"Client ID {client_id} not found")

    # Сброс для выбора другого подключения
    def reset_current_connection(self):
        """ Сбрасывает текущее активное подключение. """
        self.current_connection_id = None

    # Отправка сообщения
    async def send_message(self, message):
        """ Отправляет сообщение текущему активному клиенту. """
        writer = self.connection_id_mapping.get(self.current_connection_id)
        if writer:
            try:
                writer.write(message.encode('utf-8'))
                await writer.drain()
            except Exception as e:
                logging.error(f"Error sending message to client ID {
                              self.current_connection_id}: {e}")
        else:
            logging.error(f"No active connection for client ID {
                          self.current_connection_id}")

    # Обработка клиента
    async def handle_client_wrapper(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """
        Обрабатывает асинхронное подключение клиента к серверу.

        Этот метод создает новый экземпляр TCPConnection для каждого подключения,
        назначает уникальный идентификатор клиенту и управляет его активностью в сервере.

        Args:
            reader (asyncio.StreamReader): Объект для чтения данных от клиента.
            writer (asyncio.StreamWriter): Объект для отправки данных клиенту.
        """

        client_id = self.next_client_id
        self.next_client_id += 1
        self.connection_id_mapping[client_id] = writer

        address = writer.get_extra_info('peername')
        logging.info(f"New client connected: {client_id} (Address: {address})")

        try:
            connection = TCPConnection(self.database_config)

            while True:  # Бесконечный цикл для обработки данных от клиента
                client_data = await connection.receive_data(reader)
                if not client_data:
                    # небольшая задержка перед следующей итерацией
                    await asyncio.sleep(1)
                    continue  # Продолжить ожидание новых данных
                logging.info(f"Received data from client {client_id} (Address: {address}): {client_data}")
                sql_query = None
                if client_data.get("header") == "update":
                    table="main_characteristics"
                    unique_key="id" 
                    sql_query=await connection.update_query(table, client_data, unique_key)
                elif client_data.get("header") == "response":
                    table="solar_statement"
                    unique_key="id"
                    sql_query=await connection.insert_query(table, client_data, unique_key)
                
                if sql_query:
                    await connection.insert_data(sql_query)
                    logging.info(f"SQL query executed:{sql_query}")

        except Exception as e:
            logging.error(f"Error handling client {client_id}: {e}")
        finally:
            # Удаление клиента из словаря активных подключений только при его отключении
            if client_id in self.active_connections:
                del self.active_connections[client_id]
                logging.info(f"Client {client_id} disconnected")
                writer.close()
                await writer.wait_closed()

    # Остановка сервера
    async def stop_server(self):
        """
        Останавливает сервер и обрабатывает все активные подключения.
        """
        self.running = False
        if self.server is not None:
            # Сообщение о закрытии сервера
            shutdown_message = {"status": "shutdown",
                                "message": "Server is shutting down."}

            # Отправка сообщения о закрытии сервера клиентам
            for client_id, writer in self.connection_id_mapping.items():
                try:
                    writer.write(json.dumps(shutdown_message).encode('utf-8'))
                    await writer.drain()
                except Exception as e:
                    logging.error(f"Error sending shutdown message to client ID {
                                  client_id}: {e}")

            # Закрытие всех подключений
            for writer in self.connection_id_mapping.values():
                writer.close()
                await writer.wait_closed()

            # Очистка списка подключений
            self.connection_id_mapping.clear()

            # Закрытие сервера
            self.server.close()
            await self.server.wait_closed()
            logging.info("Server has been stopped.")


# Класс TCP подключения
class TCPConnection(AbstractTCP.AbstractTCPConnection):
    def __init__(self, database_config: dict):
        """
        Инициализирует экземпляр TCPConnection с конфигурацией базы данных.

        Args:
            database_config (dict): Конфигурация подключения к базе данных.
        """
        self.database_config = database_config

    # Обработка клиента
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
        client_id = f"{address[0]}:{address[1]}"
        try:
            logging.info(f"Starting handle for {address}")
            server.active_connections[client_id] = writer

            while True:
                data = await self.receive_data(reader)
                if not data:
                    logging.info(
                        f"Waiting for new data from client {address}.")
                    continue  # Продолжить ожидание новых данных

                # Обработка полученных данных
                data['ip_address'] = address[0]
                data['port'] = str(address[1])
                logging.info(f"Data: {data}")

                # Вставка и отправка данных
                await self.insert_data(data)
                record = await self.fetch_record(data['id'])
                await self.send_record(client_id, record, server)

        except Exception as e:
            self.log_exception(e)
        finally:
            # Этот блок кода теперь выполняется только при закрытии соединения клиентом
            if client_id in server.active_connections:
                del server.active_connections[client_id]
                logging.info(f"Closing connection for {address}")
                writer.close()
                await writer.wait_closed()

    # Отправление данных
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

    # Обработка принятых данных
    async def receive_data(self, reader: asyncio.StreamReader) -> dict:
        """
        Асинхронно получает и обрабатывает данные от клиента.

        Этот метод читает данные, отправленные клиентом, декодирует их из формата
        байт в строку, затем преобразует строку JSON в словарь Python.

        Args:
            reader (asyncio.StreamReader): Объект StreamReader для чтения данных от клиента.

        Returns:
            dict: Словарь, содержащий данные, полученные от клиента, или пустой словарь, если произошла ошибка.
        """
        try:
            # Чтение данных до символа новой строки
            raw_data = await reader.readuntil(b'\n')
            logging.info(f"Raw data: {raw_data!r}")  # Вывод сырых данных

            # Декодирование данных из байтов в строку
            decoded_data = raw_data.decode('utf-8').strip()
            # Вывод декодированных данных
            logging.info(f"Decoded data: {decoded_data}")

            # Конвертация строки JSON в словарь Python
            json_data = json.loads(decoded_data)
            logging.info(f"JSON data: {json_data}")  # Вывод JSON данных
            return json_data
        # Клиент отключился до отправки новой строки
        except asyncio.IncompleteReadError:
            # Логируем информацию о клиенте, который отключился
            client_address = reader.get_extra_info('peername')
            logging.info("Client disconnected before sending a newline.")
            # Отключаем клиента методом
            await self.client_disconnect(client_address)
            return {}

        except json.JSONDecodeError as e:
            # Ошибка декодирования JSON
            self.log_exception(f"Received data is not valid JSON: {e}")
            return {}

        except Exception as e:
            # Любые другие исключения
            self.log_exception(f"An exception occurred: {e}")
            return {}

    async def insert_data(self, query: str, *args) -> None:
        """
        Выполняет SQL-запрос с заданными аргументами.

        Этот метод асинхронно подключается к базе данных, выполняет предоставленный SQL-запрос
        с аргументами и затем закрывает соединение.

        Args:
            query (str): Строка SQL-запроса для выполнения.
            args: Аргументы, которые необходимо передать в SQL-запрос.
        """
        try:
            logging.info("Connecting to DB...")
            conn = await asyncpg.connect(**self.database_config)
            logging.info("Connected to DB. Executing query...")

            # Выполнение SQL-запроса
            await conn.execute(query, *args)
            logging.info("Query executed successfully.")
        except Exception as e:
            self.log_exception(e)
        finally:
            # Закрытие соединения с базой данных
            await conn.close()
            logging.info("DB connection closed.")

    async def insert_query(self, table: str, data: dict) -> str:
        """
        Генерирует SQL-запрос INSERT.

        Args:
        table (str): Название таблицы в базе данных.
        data (dict): Словарь с данными для вставки.

        Returns:
        str: Строка SQL-запроса для вставки данных.
        """
        # Исключаем ключ 'header' из словаря
        filtered_data = {k: v for k, v in data.items() if k != "header"}

        columns = ', '.join(filtered_data.keys())
        values = ', '.join([f"'{v}'" for v in filtered_data.values()])

        insert_query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
        logging.info(f"Generated INSERT query: {insert_query}")
        return insert_query

    async def update_query(self, table: str, data: dict, unique_key: str) -> str:
        """
        Генерирует SQL-запрос UPDATE.

        Args:
        table (str): Название таблицы в базе данных.
        data (dict): Словарь с данными для обновления.
        unique_key (str): Ключ для проверки уникальности записи.

        Returns:
        str: Строка SQL-запроса для обновления данных.
        """
        # Исключаем ключ 'header' и unique_key из словаря
        filtered_data = {k: v for k, v in data.items() if k != "header" and k != unique_key}

        update_parts = [f"{key} = '{value}'" for key, value in filtered_data.items()]
        update_query = f"UPDATE {table} SET {', '.join(update_parts)} WHERE {unique_key} = '{data[unique_key]}'"
        logging.info(f"Generated UPDATE query: {update_query}")
        return update_query

    # Обработка отключения клиента
    async def client_disconnect(self, client_address: Tuple[str, int]) -> None:
        """
        Обрабатывает отключение клиента.

        Этот метод закрывает StreamWriter для указанного клиента и удаляет его из словаря
        активных подключений сервера. Если клиент уже был отключен или не найден, 
        записывает соответствующее сообщение в лог.

        Args:
            client_address (Tuple[str, int]): Адрес клиента в формате (IP, порт).
        """
        # Находим client_id по адресу
        client_id = next((id for id, writer in self.active_connections.items() 
                          if writer.get_extra_info('peername') == client_address), None)

        if client_id:
            writer = self.active_connections[client_id]
            writer.close()
            await writer.wait_closed()
            logging.info(f"Client {client_id} at {client_address} has been disconnected and removed.")

            # Удаляем клиента из словаря активных подключений
            del self.active_connections[client_id]
        else:
            logging.info(f"Client at {client_address} already disconnected or not found.")

    # async def fetch_record(self, record_id: int) -> dict:
    #     try:
    #         conn = await asyncpg.connect(**self.database_config)
    #         record = await conn.fetchrow(
    #             'SELECT * FROM main_solar_panel WHERE id = $1',
    #             record_id
    #         )
    #         # Конвертируем Record в словарь перед возвращением
    #         return dict(record) if record else {}
    #     except Exception as e:
    #         self.log_exception(e)
    #         return {}

    def log_exception(self, exception: Exception) -> None:
        logging.exception(f"An exception occurred: {exception}")
