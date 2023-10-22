from django.db import models

class Solar_Panel(models.Model):
    installation_number = models.IntegerField(primary_key=True)
    ip_address = models.CharField(max_length=15, default='')
    port = models.CharField(max_length=5, default='')

    class Meta:
        ordering = ['-installation_number']

    def __str__(self):
        return str(self.installation_number)

class Characteristics(models.Model):
    date = models.DateField()
    time = models.TimeField()
    generated_power = models.FloatField()
    consumed_power = models.FloatField()
    vertical_position = models.IntegerField()
    horizontal_position = models.IntegerField()
    solar_panel = models.ForeignKey(Solar_Panel, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-date', 'time']

    def __str__(self):
        return str(self.date)

