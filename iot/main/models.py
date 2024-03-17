from django.db import models

# Модель для представления солнечных панелей
class Solar_Panel(models.Model):
    id = models.IntegerField(primary_key=True)  # id установки
    ip_address = models.CharField(max_length=15, default='')  # адрес
    port = models.CharField(max_length=5, default='')  # порт установки
    coordinates = models.CharField(null=True, blank=True)  # координаты
    description = models.TextField(null=True, blank=True)  # описание
    type = models.TextField(null=True, blank=True)  # тип установки (поворотная/неповоротная)


    class Meta:
        ordering = ['-id'] # Сортировка по убыванию id при запросах к модели

    def __str__(self):
        return str(self.id) # Возвращаем строковое представление id установки


# Модель для хранения характеристик солнечных панелей
class Characteristics(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    time = models.TimeField()
    generated_power = models.FloatField()
    consumed_power = models.FloatField()
    vertical_position = models.IntegerField()
    horizontal_position = models.IntegerField()
    status = models.TextField(null=True, blank=True)  # on off etc
    options = models.TextField(null=True, blank=True)  # в заметках
    weather = models.TextField(null=True, blank=True)  # берется с сайта
    battery = models.FloatField(null=True)  # заряд батареи

    solar_panel = models.ForeignKey(
        Solar_Panel, on_delete=models.RESTRICT, null=True, blank=True) # Связь с соответствующей солнечной панелью

    class Meta:
        ordering = ['-date', 'time'] # Сортировка по убыванию даты и возрастанию времени записи

    def __str__(self):
        return str(self.date) # Возвращаем строковое представление даты характеристики


# Модель для хранения заявлений и команд относительно солнечных панелей
class SolarStatement(models.Model):
    solar_panel = models.ForeignKey(Solar_Panel, on_delete=models.RESTRICT) # Связь с соответствующей солнечной панелью
    id = models.AutoField(primary_key=True)  # Уникальный идентификатор заявления
    statement = models.TextField() # Заявление
    command = models.TextField() # Команда
    date = models.DateTimeField() # Дата и время заявления

    class Meta:
        db_table = 'solar_statement' # Имя таблицы в базе данных

    def __str__(self):
        return f"Statement {self.id} from Solar {self.solar_panel}" # Возвращаем строковое представление заявления и связанной с ним солнечной панели
