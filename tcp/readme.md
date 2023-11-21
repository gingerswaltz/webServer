Класс TCPServer
Наследуется от AbstractTCP.AbstractTCPServer и представляет собой TCP сервер для асинхронного взаимодействия с клиентами и обработки данных.

Атрибуты:
server: Объект сервера asyncio.Server. Отвечает за управление асинхронными подключениями.
active_connections: Словарь, хранящий активные подключения (ключ - ID клиента, значение - объект StreamWriter).
connection_id_mapping: Словарь, соотносящий ID клиента с его StreamWriter. Используется для отправки сообщений определённым клиентам.
next_client_id: Счетчик ID клиентов. Используется для присвоения уникального идентификатора каждому новому клиенту.
current_connection_id: ID текущего активного подключения. Используется для отправки сообщений выбранному клиенту.
running: Флаг, указывающий на состояние работы сервера.
Методы:
__init__(self, host: str, port: int, database_config: Dict[str, Any]):

Конструктор класса.
host: Строка, определяющая хост для сервера.
port: Целое число, указывающее порт для сервера.
database_config: Словарь с конфигурацией для подключения к базе данных.
async start_server(self):

Запускает сервер и управляет его асинхронной работой.
Включает в себя цикл, который работает до тех пор, пока флаг running не станет False.
set_active_connection(self, client_id):

Устанавливает активное подключение для взаимодействия с определенным клиентом.
client_id: ID клиента для активации подключения.
reset_current_connection(self):

Сбрасывает текущее активное подключение.
async send_message(self, message):

Отправляет сообщение текущему активному клиенту.
message: Сообщение, которое необходимо отправить.
async handle_client_wrapper(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):

Обрабатывает подключение каждого нового клиента.
Создаёт уникальный ID для клиента и управляет его подключением.
async stop_server(self):

Останавливает сервер и обрабатывает все активные подключения.
Отправляет сообщение о закрытии сервера всем подключённым клиентам и закрывает их соединения.

________________________________________________________________________

Класс TCPConnection
Наследуется от AbstractTCP.AbstractTCPConnection и представляет собой класс для управления TCP соединениями на стороне сервера.

Атрибуты:
database_config (dict): Конфигурация для подключения к базе данных.
Методы:
__init__(self, database_config: dict):

Конструктор класса.
Инициализирует объект с заданной конфигурацией базы данных.
async handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, address: Tuple[str, str], server: TCPServer) -> None:

Обрабатывает каждое подключение клиента.
Регистрирует подключение, читает данные, вставляет их в базу данных и отправляет ответы.
reader: Объект StreamReader для чтения данных.
writer: Объект StreamWriter для отправки данных.
address: Адрес клиента (IP и порт).
server: Экземпляр TCPServer для управления подключениями.
async send_record(self, client_id: str, data: Any, server: TCPServer) -> None:

Отправляет данные указанному клиенту.
client_id: Идентификатор клиента.
data: Данные для отправки.
server: Экземпляр сервера для доступа к активным подключениям.
async receive_data(self, reader: asyncio.StreamReader) -> dict:

Получает и обрабатывает данные от клиента.
Возвращает словарь с данными или пустой словарь при ошибке.
async insert_data(self, query: str, *args) -> None:

Выполняет SQL-запрос в базе данных.
query: SQL-запрос для выполнения.
args: Аргументы для SQL-запроса.
async check_query(self, table: str, data: dict, unique_key: str) -> (str, list):

Генерирует SQL-запрос для вставки или обновления данных.
Возвращает строку SQL-запроса и список аргументов.
async client_disconnect(self, client_id: str, server: TCPServer) -> None:

Обрабатывает отключение клиента.
client_id: Идентификатор клиента для отключения.
server: Экземпляр сервера для управления подключениями.
async fetch_record(self, record_id: int) -> dict:

Получает запись из базы данных по идентификатору.
Возвращает словарь с данными записи или пустой словарь.
log_exception(self, exception: Exception) -> None:

Логгирует исключения.
exception: Исключение для логгирования.
