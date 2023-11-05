import socket
import asyncio
import json
import asyncpg
from AbstractTCP import AbstractTCPServer
from AbstractTCP import AbstractTCPConnection

# Класс TCP подключения
class TCPConnection(AbstractTCPConnection):
    
    def __init__(self, host, port, database_connection, client_socket, client_address):
        super().__init__(host, port)
        self._database_connection=database_connection
        self.client_socket=client_socket;
        self.client_address=client_address;
    
    
    #инициализация подключения
    async def _initialize_connection(self):
        try:
            self.server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(self.host, self.port)
            self.server_socket.listen(1)
            self.client_socket, self.client_address=self.server_socket.accept()
        except Exception as e:
            return str(e)
    
    #обработка подключения
    async def handle_client(self):
        try:
            self._initialize_connection()
            data=await self._receive_data(self.client_socket)
            request=json.loads(data)
        # Запись данных в базу данных PostgreSQL
            self._insert_data(request, "")
            self._receive_data(self.client_socket)
        except Exception as e:
            return str(e)
        finally:
            # После выполнения основной логики (успешно или с ошибкой)
            self.handle_client_disconnect(self.client_socket)
    
    
    
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
            return str(e)
    
    #вставка данных в БД
    async def _insert_data(self, data, table_name):
        try:
         conn = await asyncpg.connect(**self. _database_connection)
         cursor = conn.cursor()

        # Пример SQL-запроса для вставки данных в таблицу
         sql = f"INSERT INTO {table_name} (column1, column2) VALUES (%s, %s)"
         values = (data["value1"], data["value2"])  # Заменить на реальные значения
         
         #*values - распаковка элементов кортежа в том порядке, как они записаны
         await conn.execute(sql, *values)
        except Exception as e:
            return str(e)
        finally: 
            return 0;
   
    #получение записи из БД
    def _fetch_record(self, record_id, table_name):
        try: 
            conn=asyncpg.connect(**self._database_connection)
            cursor=conn.cursor();
            sql=f"SELECT * from {table_name} WHERE id=%s"
            values=(record_id, )
            cursor.execute();
            record=cursor.fetchone();
            cursor.close();
            conn.close();
            return record;
        except Exception as e:
            return str(e)
        

    #отправка записи из БД клиенту
    async def _send_record(self, record):
       try:
        record_json=json.dumps(record);
        await self.client_socket.send(record_json.encode("utf-8"));
       except Exception as e:
           return str(e)
       

    def handle_client_disconnect(self):
        # Реализация обработки отключения клиента
        str=(f"Клиент {self.client_socket.getpeername()} отключился")
        self.client_socket.close()
        return(str)