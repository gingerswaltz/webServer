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
        self.connections_mapping = {}  # Добавляем новый словарь для связи с TCPConnection
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

    async def send_message(self, message):
        connection = self.connections_mapping.get(self.current_connection_id)
        if connection:
            try:
                client_data = await connection.send_record(message)
                if client_data:
                    table = "solar_statement"
                    sql_query = await connection.insert_query(table, client_data)
                    if sql_query:
                        await connection.insert_data(sql_query)
                        logging.info(f"SQL query executed:{sql_query}")
            except Exception as e:
                logging.error(f"Error sending message to client ID {self.current_connection_id}: {e}")
        else:
            logging.error(f"No connection found for client ID {self.current_connection_id}")

    # Обработка клиента
    async def handle_client_wrapper(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        client_id = self.next_client_id
        self.next_client_id += 1
        self.connection_id_mapping[client_id] = writer

        connection = TCPConnection(self.database_config, reader, writer, client_id)  # Изменено
        self.connections_mapping[client_id] = connection  # Сохраняем связь
        
        address = writer.get_extra_info('peername')
        
        logging.info(f"New client connected: {client_id} (Address: {address})")

        try:
            while True:  # Бесконечный цикл для обработки данных от клиента
                client_data = await connection.receive_data()
                if not client_data:
                    # небольшая задержка перед следующей итерацией
                    await asyncio.sleep(1)
                    continue  # Продолжить ожидание новых данных
                
                # Извлекаем id из client_data
                client_id_value = client_data.get('id')

                # Формируем словарь с адресом и id
                address_dict = {
                "id": client_id_value,
                "ip_address": address[0],
                "port": address[1]
                }
                
                if client_data.get("header") == "update":
                    sql_query=await connection.update_query("main_solar_panel", address_dict, "id")
                    await connection.insert_data(sql_query)
                    table="main_characteristics"
                    unique_key="id" 
                    sql_query=await connection.update_query(table, client_data, unique_key)
                
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
    def __init__(self, database_config: dict, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, client_id: str):
        self.database_config = database_config
        self.reader = reader
        self.writer = writer
        self.client_id = client_id

    # Обработка клиента
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, address: Tuple[str, str], server: TCPServer) -> None:
    
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
                
        except Exception as e:
            self.log_exception(e)
        finally:
            # Этот блок кода теперь выполняется только при закрытии соединения клиентом
            if client_id in server.active_connections:
                del server.active_connections[client_id]
                logging.info(f"Closing connection for {address}")
                writer.close()
                await writer.wait_closed()

    async def send_record(self, message: str) -> dict:
        try:
            # Отправляем сообщение
            self.writer.write(message.encode('utf-8'))
            await self.writer.drain()

            # Чтение ответа
            data = await self.reader.read(4096)
            if not data:
                logging.info("No response received from the client.")
                return None

            response = data.decode()
            logging.info(f"Received response from client {self.client_id}: {response}")
            return json.loads(response)
        except Exception as e:
            self.log_exception(e)
            return None

    # Обработка принятых данных
    async def receive_data(self) -> dict:
        try:
            # Чтение данных до символа новой строки
            raw_data = await self.reader.readuntil(b'\n')
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
            client_address = self.reader.get_extra_info('peername')
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
        
        # Исключаем ключ 'header' из словаря
        filtered_data = {k: v for k, v in data.items() if k != "header"}

        columns = ', '.join(filtered_data.keys())
        values = ', '.join([f"'{v}'" for v in filtered_data.values()])

        insert_query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
        logging.info(f"Generated INSERT query: {insert_query}")
        return insert_query

    async def update_query(self, table: str, data: dict, unique_key: str) -> str:
        
        # Исключаем ключ 'header' и unique_key из словаря
        filtered_data = {k: v for k, v in data.items() if k != "header" and k != unique_key}

        update_parts = [f"{key} = '{value}'" for key, value in filtered_data.items()]
        update_query = f"UPDATE {table} SET {', '.join(update_parts)} WHERE {unique_key} = '{data[unique_key]}'"
        logging.info(f"Generated UPDATE query: {update_query}")
        return update_query

    # Обработка отключения клиента
    async def client_disconnect(self, client_address: Tuple[str, int]) -> None:
        
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
            
    def log_exception(self, exception: Exception) -> None:
        logging.exception(f"An exception occurred: {exception}")
