from django.db import models
#todo: doc

class Solar_Panel(models.Model):
    id = models.IntegerField(primary_key=True)
    ip_address = models.CharField(max_length=15, default='')
    port = models.CharField(max_length=5, default='')
    # coordinates 
    # description
    # тип установки (поворот не поворот)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return str(self.id)


class Characteristics(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    time = models.TimeField()
    generated_power = models.FloatField()
    consumed_power = models.FloatField()
    vertical_position = models.IntegerField()
    horizontal_position = models.IntegerField()
    # status (on off etc)
    # options (прописаны в заметках)
    # погода (солнце, ветренность, температура, влажность)
    # заряд акб
    solar_panel = models.ForeignKey(Solar_Panel, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-date', 'time']

    def __str__(self):
        return str(self.date)
    

class SolarStatement(models.Model):
    solar_panel = models.ForeignKey(Solar_Panel, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    statement = models.TextField()
    command=models.TextField()
    date = models.DateTimeField()
    
    class Meta:
        db_table = 'solar_statement' 

    def __str__(self):
        return f"Statement {self.id} from Solar {self.solar_panel}"

