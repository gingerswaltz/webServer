from abc import ABC, abstractmethod
import asyncio
from typing import Any, Dict, Tuple
import socket


class AbstractTCPServer(ABC):
    def __init__(self, host: str, port: int, database_config: Dict[str, Any]):
        self.host = host
        self.port = port
        self.database_config = database_config

    @abstractmethod
    async def start_server(self) -> None:
        """
        Запускает сервер, который слушает входящие подключения на заданном хосте и порте.
        """
        pass

    @abstractmethod
    async def handle_client_wrapper(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """
        Функция-обертка для обработки клиентского подключения. Должна создать экземпляр TCPConnection
        и вызвать его метод handle_client.
        """
        pass

    @abstractmethod
    async def stop_server(self) -> None:
        """
        Останавливает сервер и закрывает все активные подключения.
        """
        pass

   
        
class AbstractTCPConnection(ABC):
    """
    Абстрактный класс, описывающий базовый интерфейс TCP соединения.
    Классы-наследники должны реализовать все абстрактные методы.
    """

    @abstractmethod
    async def handle_client(self, client_socket: socket.socket, address: Tuple[str, int]) -> None:
        """
        Обрабатывает входящее соединение от клиента.
        Должен быть реализован для чтения записи из базы данных,
        отслеживания изменений и отправки данных клиенту.
        """
        pass

    @abstractmethod
    async def send_record(self, client_socket: socket.socket, data: Any) -> None:
        """
        Отправляет измененную запись клиенту через его TCP-сокет.
        """
        pass

    @abstractmethod
    async def receive_data(self, client_socket: socket.socket) -> Any:
        """
        Получает данные от клиента через TCP-сокет.
        """
        pass

    @abstractmethod
    async def insert_data(self, data: Any) -> None:
        """
        Добавляет или обновляет запись в базе данных на основе данных, полученных от клиента.
        """
        pass

   
    @abstractmethod
    def log_exception(self, exception: Exception) -> None:
        """
        Логирует исключения, возникающие в процессе работы соединения.
        """
        pass