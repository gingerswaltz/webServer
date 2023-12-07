import requests
import sys

SERVER_URL = "http://127.0.0.1:8080"

def get_connected_clients():
    response = requests.get(f"{SERVER_URL}/clients")
    if response.ok:
        print(response.json())
    else:
        print("Ошибка при получении списка клиентов")

def set_active_client(client_id):
    response = requests.post(f"{SERVER_URL}/set_active_client", json={"client_id": client_id})
    if response.ok:
        print("Активный клиент установлен")
    else:
        print("Ошибка при установке активного клиента")

def send_message_to_client(message):
    response = requests.post(f"{SERVER_URL}/send_message", json={"message": message})
    if response.ok:
        print("Сообщение отправлено")
    else:
        print("Ошибка при отправке сообщения")


def user_interface():
    try:
        while True:
            print("\nДоступные команды:")
            print("1: Показать список подключенных клиентов")
            print("2: Выбрать клиента для отправки сообщения")
            print("3: Отправить сообщение выбранному клиенту")
            choice = input("Введите команду: ")

            if choice == '1':
                get_connected_clients()
            elif choice == '2':
                client_id = input("Введите ID клиента: ")
                set_active_client(int(client_id))
            elif choice == '3':
                message = input("Введите сообщение: ")
                send_message_to_client(message)
    except Exception as e:
        print(e)
    finally:
        sys.exit(0);

if __name__ == "__main__":
    try:
        user_interface()
    except Exception as e:
        print(e)
