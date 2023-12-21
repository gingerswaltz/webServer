import asyncio
import time
import asyncpg
import json
from typing import Any, Tuple
import AbstractTCP
import logging
from typing import Any, Dict


# Класс TCP Сервера
class TCPServer(AbstractTCP.AbstractTCPServer):
    def __init__(self, host: str, port: int, database_config: Dict[str, Any], disconnection_callback=None, connection_callback=None):
        super().__init__(host, port, database_config)
        self.server = None
        self.active_connections = {}  # Словарь активных подключений
        self.current_connection_id = None  # Текущее активное подключение
        self.connections_mapping = {}  # Добавляем новый словарь для связи с TCPConnection
        self.running = False  # Флаг состояния работы
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        # Callback для уведомления интерфейсов об отключении
        self.disconnection_callback = disconnection_callback
        # Callback для уведомления интерфейсов о подключении
        self.connection_callback = connection_callback

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
        writer = self.connections_mapping.get(int(client_id))
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
                await connection.send_message_only(message)
                # Обратите внимание, что здесь нет чтения ответа, это происходит в `listen_for_messages`
            except Exception as e:
                logging.error(f"Error sending message to client ID {self.current_connection_id}: {e}")
                await self.client_disconnect(self.current_connection_id)
        else:
            logging.error(f"No connection found for client ID {self.current_connection_id}")


    # Обработка клиента
    async def handle_client_wrapper(self, reader, writer):
        # Создаем временный уникальный идентификатор для нового подключения
        temp_client_id = f"temp_{time.time()}_{writer.get_extra_info('peername')}"

        # Создание нового подключения
        connection = TCPConnection(self.database_config, reader, writer, temp_client_id, self)
        self.connections_mapping[temp_client_id] = connection

        # Запись адреса клиента
        address = writer.get_extra_info('peername')
        logging.info(f"New client connected: {temp_client_id} (Address: {address})")
        
        # Запуск фоновой корутины для чтения сообщений и ожидания сообщения `update`
        asyncio.create_task(connection.listen_for_messages())



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
            for client_id, writer in self.connections_mapping.items():
                try:
                    writer.write(json.dumps(shutdown_message).encode('utf-8'))
                    await writer.drain()
                except Exception as e:
                    logging.error(f"Error sending shutdown message to client ID {
                                  client_id}: {e}")

            # Закрытие всех подключений
            for writer in self.connections_mapping.values():
                writer.close()
                await writer.wait_closed()

            # Очистка списка подключений
            self.connections_mapping.clear()

            # Закрытие сервера
            self.server.close()
            await self.server.wait_closed()
            logging.info("Server has been stopped.")
    
    
    async def client_disconnect(self, client_id):
        if client_id in self.connections_mapping:
            del self.connections_mapping[client_id]
            logging.info(f"Client {client_id} removed from connections_mapping.")

        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logging.info(f"Client {client_id} removed from active_connections.")
        
        if self.disconnection_callback:
            await self.disconnection_callback(client_id)
    
    def update_client_mappings(self, old_id, new_id):
        """Обновление маппингов клиента после получения нового ID"""
        if old_id in self.connections_mapping:
            self.connections_mapping[new_id] = self.connections_mapping.pop(old_id)
        
        if old_id in self.active_connections:
            self.active_connections[new_id] = self.active_connections.pop(old_id)
        
        logging.info(f"Client mappings updated from {old_id} to {new_id}")
        # Вызов callback для уведомления о подключении клиента
        if self.connection_callback:
            asyncio.create_task(self.connection_callback(new_id))


# Класс TCP подключения
class TCPConnection(AbstractTCP.AbstractTCPConnection):
    def __init__(self, database_config: dict, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, client_id: str, server: TCPServer):
        self.database_config = database_config
        self.reader = reader
        self.writer = writer
        self.client_id = client_id
        self.data_queue = asyncio.Queue()
        self.server=server
    
    def update_client_id(self, new_client_id):
        old_client_id = self.client_id
        self.client_id = new_client_id
        self.server.update_client_mappings(old_client_id, new_client_id)
        logging.info(f"Client ID updated from {old_client_id} to {new_client_id}")




    async def send_message_only(self, message: str):
        try:
            self.writer.write(message.encode('utf-8'))
            await self.writer.drain()
        except Exception as e:
            self.log_exception(e)
    
    async def listen_for_messages(self):
        try:
            while True:
                data = await self.reader.read(4096)
                if not data:
                    break  # Соединение закрыто, выходим из цикла

                response = data.decode()
                json_data = json.loads(response)

                # Обработка json_data
                if json_data.get("header") == "response":
                    # Обработка ответа
                    table = "solar_statement"
                    sql_query = await self.insert_query(table, json_data)
                    if sql_query:
                        await self.insert_data(sql_query)
                        logging.info(f"SQL query executed:{sql_query}")
                elif json_data.get("header") == "update":
                    # Обработка обновления
                    client_id_value = json_data.get('id')
                
                    if client_id_value:
                        self.update_client_id(client_id_value)
                        address = self.writer.get_extra_info('peername')
                        address_dict = {
                        "id": client_id_value,
                        "ip_address": address[0],
                        "port": address[1]
                        }
                        sql_query = await self.update_query("main_solar_panel", address_dict, "id")
                        if sql_query:
                            await self.insert_data(sql_query)
                            logging.info(f"SQL query executed:{sql_query}")

                        table = "main_characteristics"
                        sql_query = await self.insert_query(table, json_data)
                        if sql_query:
                            await self.insert_data(sql_query)
                    else:
                        logging.error("Key 'id' not found in json_data")
        
        except ConnectionResetError:
        # Обработка неожиданного отключения клиента
            logging.info(f"Client {self.client_id} has disconnected unexpectedly.")
            self.handle_client_disconnection()
        except Exception as e:
            self.log_exception(e)
        finally:
            # Закрытие соединения, если необходимо
            self.writer.close()
            await self.writer.wait_closed()
            self.handle_client_disconnection()

    def handle_client_disconnection(self):
        # Вызываем метод client_disconnect сервера для обработки отключения клиента
        asyncio.create_task(self.server.client_disconnect(self.client_id))

        

    async def start_reading(self):
        """ Чтение данных из reader и помещение их в очередь. """
        while True:
            data = await self.reader.read(4096)
            if not data:
                break  # Поток закрыт, выходим из цикла
            await self.data_queue.put(data)

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

    async def send_record(self, message:     str) -> dict:
        try:
            # Отправляем сообщение
            self.writer.write(message.encode('utf-8'))
            await self.writer.drain()

            # Ожидаем ответа из очереди
            try:
                response_data = await asyncio.wait_for(self.data_queue.get(), timeout=10.0)  # Задаем таймаут
            except asyncio.TimeoutError:
                logging.info("Timeout waiting for response from the client.")
                return None

            if not response_data:
                logging.info("No response received from the client.")
                return None

            response = response_data.decode()
            logging.info(f"Received response from client {self.client_id}: {response}")
            return json.loads(response)
        except Exception as e:
            self.log_exception(e)
            return None


    # Обработка принятых данных
    async def receive_data(self):
        try:
            while True:
                # Чтение данных до символа новой строки
                raw_data = await self.reader.readuntil(b'\n')
                logging.info(f"Raw data: {raw_data!r}")

                # Декодирование данных из байтов в строку
                decoded_data = raw_data.decode('utf-8').strip()
                logging.info(f"Decoded data: {decoded_data}")

                # Конвертация строки JSON в словарь Python
                json_data = json.loads(decoded_data)
                logging.info(f"JSON data: {json_data}")

                # Помещаем данные в очередь
                await self.data_queue.put(json_data)

        except asyncio.IncompleteReadError:
            client_address = self.reader.get_extra_info('peername')
            logging.info("Client disconnected before sending a newline.")
            await self.client_disconnect(client_address)

        except json.JSONDecodeError as e:
            self.log_exception(f"Received data is not valid JSON: {e}")

        except Exception as e:
            self.log_exception(f"An exception occurred: {e}")

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
        filtered_data = {k: v for k, v in data.items() if k != "header" and k!="id"}

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