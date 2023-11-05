import socket
import asyncio
import json
import asyncpg
import logging
from AbstractTCP import AbstractTCPServer
from AbstractTCP import AbstractTCPConnection

# Класс TCP подключения
class TCPConnection(AbstractTCPConnection):
    
    def __init__(self, host, port, database_connection, client_socket, client_address):
        super().__init__(host, port)
        self._database_connection=database_connection
        self.client_socket=client_socket;
        self.client_address=client_address;
        logging.basicConfig(filename='connections.log', level=logging.ERROR)
    
    #инициализация подключения
    async def _initialize_connection(self):
        try:
            self.server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(self.host, self.port)
            self.server_socket.listen(1)
            self.client_socket, self.client_address=self.server_socket.accept()
        except Exception as e:
            self.log_exception(e)
            raise e
    
    #обработка подключения
    async def handle_client(self):
        try:
            self._initialize_connection()
            data=await self._receive_data(self.client_socket)
            request=json.loads(data)
        # Запись данных в базу данных PostgreSQL
            self._insert_data(request, "")
        except Exception as e:
            self.log_exception(e)
            raise e
        finally:
            self._client_disconnect(self.client_socket)
    
    
    
    #получение данных от клиента
    async def _receive_data(self):
        try:
            data=b""
            while True:
                chunk=await self.client_socket.recv(1024)
                if not chunk:
                    break
                data+=chunk
            return data.decode("utf-8")
        except Exception as e:
            self.log_exception(e)
            raise e
    
    #вставка данных в БД
    async def _insert_data(self, data, table_name):
        try:
         conn = await asyncpg.connect(**self. _database_connection)
         sql = f"INSERT INTO {table_name} (column1, column2) VALUES (%s, %s)"
         values = (data["value1"], data["value2"])  # Заменить на реальные значения

         # *values - распаковка элементов кортежа в том порядке, как они записаны
         await conn.execute(sql, *values)
        except Exception as e:
            self.log_exception(e)
            raise e 
        finally: 
            await conn.close();
   
    #получение записи из БД
    async def _fetch_record(self, record_id, table_name):
        try: 
            # ** - распаковка словаря.
            conn= await asyncpg.connect(**self._database_connection)
            sql=f"SELECT * from {table_name} WHERE id=%s"
            values=(record_id, )
            await conn.execute(sql, *values);
            record= await conn.fetchone();
            return record;
        except Exception as e:
            self.log_exception(e)
            raise e
        finally:
           await conn.close();


    #отправка записи из БД клиенту
    async def _send_record(self, record):
       try:
        record_json=json.dumps(record);
        await self.client_socket.send(record_json.encode("utf-8"));
       except Exception as e:
           self.log_exception(e)
           raise e  
       
    #обработка отключения клиента
    async def _client_disconnect(self):
        str=(f"Клиент {self.client_socket.getpeername()} отключился")
        await self.client_socket.close() # закрытие соединения
        return(str)

     # Метод логгирования
    def log_exception(self, exception):
        logger = logging.getLogger(__name__) # экземпляр объекта логгера
        logger.exception("An exception occurred: %s", exception) # запись ошибки в логгер. логгер по умолчанию записывает в файл connections.log