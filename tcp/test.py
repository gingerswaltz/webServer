from socket import socket
import unittest
import pytest
from unittest.mock import MagicMock
from TCPServer import TCPConnection


def test_connection_init_succ():
    host="127.0.0.1"
    port=8080
    database_connection = {"user": "user", "password": "password", "database": "db"}
    client_socket = None 
    client_address = ("127.0.0.1", 12345)  # Замените на адрес клиента
    
    connection = TCPConnection(host, port, database_connection, client_socket, client_address)

    assert connection.host == host
    assert connection.port == port
    assert connection._database_connection == database_connection
    assert connection.client_socket == client_socket
    assert connection.client_address == client_address


def test_initialize_connection_success():
    host = "127.0.0.1"
    port = 8080
    database_connection = {"user": "user", "password": "password", "database": "db"}
    client_socket = None  # Замените на ваш сокет
    client_address = ("127.0.0.1", 12345)  # Замените на адрес клиента

    connection = TCPConnection(host, port, database_connection, client_socket, client_address)

    connection._initialize_connection()

    assert connection.server_socket is not None
    assert connection.client_socket is not None
    assert connection.client_address is not None

def test_initialize_connection_socket_error():
    host = "invalid_host"
    port = 8080
    database_connection = {"user": "user", "password": "password", "database": "db"}
    client_socket = None
    client_address = ("127.0.0.1", 12345)

    connection = TCPConnection(host, port, database_connection, client_socket, client_address)

    with pytest.raises(socket.error):
        connection._initialize_connection()

def test_initialize_connection_listen_error():
    host = "127.0.0.1"
    port = 8080
    database_connection = {"user": "user", "password": "password", "database": "db"}
    client_socket = None
    client_address = ("127.0.0.1", 12345)

    connection = TCPConnection(host, port, database_connection, client_socket, client_address)

    # Меняем хост и порт серверного соксета на некорректные
    connection.server_socket.bind("invalid_host", "invalid_port")

    with pytest.raises(socket.error):
        connection._initialize_connection()

def test_initialize_connection_server_socket_closed():
    host = "127.0.0.1"
    port = 8080
    database_connection = {"user": "user", "password": "password", "database": "db"}
    client_socket = None
    client_address = ("127.0.0.1", 12345)

    connection = TCPConnection(host, port, database_connection, client_socket, client_address)

    connection._initialize_connection()

    assert connection.server_socket is not None
    assert not connection.server_socket._closed
