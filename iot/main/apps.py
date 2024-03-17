from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField' # Используем тип BigAutoField для автоматического поля первичного ключа
    name = 'main' # Имя приложения
