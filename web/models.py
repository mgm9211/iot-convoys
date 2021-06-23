from django.db import models

# Create your models here.


class Device(models.Model):
    name = models.CharField(max_length=16, blank=True, null=False, unique=True)
    is_master = models.BooleanField()

    def last_record(self):
        return Information.objects.filter(device=self).last()


# {'Data': '27.06;43.00;120.00;36.715508;-4.553879', 'Timestamp': 280056, 'ID': 'SoyElMaster'}
class Information(models.Model):
    device = models.ForeignKey(Device, models.DO_NOTHING, blank=True, null=True)
    temp = models.FloatField(null=False, blank=True)
    hum = models.FloatField(null=False, blank=True)
    lat = models.FloatField(null=False, blank=True)
    lon = models.FloatField(null=False, blank=True)
    speed = models.FloatField(null=False, blank=True)
    timestamp = models.DateTimeField()