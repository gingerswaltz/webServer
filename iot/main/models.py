from django.db import models

class Reading(models.Model):
    id = models.AutoField(primary_key=True)
    installation_number = models.IntegerField()
    date = models.DateField()
    time = models.TimeField()
    generated_power = models.FloatField()
    consumed_power = models.FloatField()
    vertical_position = models.IntegerField()
    horizontal_position = models.IntegerField()