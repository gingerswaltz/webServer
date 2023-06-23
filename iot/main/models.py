from django.db import models

class Reading(models.Model):
    installation_number = models.IntegerField(primary_key=True)
    date = models.DateField()
    time = models.TimeField()
    generated_power = models.FloatField()
    consumed_power = models.FloatField()
    vertical_position = models.IntegerField()
    horizontal_position = models.IntegerField()
    ip = models.ForeignKey('Ip', on_delete=models.CASCADE, null=True, blank=True)

class Ip(models.Model):
    ip_address = models.CharField(max_length=15, default='')
    port = models.CharField(max_length=5, default='')
