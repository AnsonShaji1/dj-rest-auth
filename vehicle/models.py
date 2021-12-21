from django.db import models
from django.utils.text import slugify
from django.contrib.postgres.fields import HStoreField
from dispatch.models import TimeStampMixin

STATUS_CHOICES = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('deleted', 'Deleted')
)

VEHICLE_CHOICE = (
    ('owned', 'Owned'),
)

class VehicleType(models.Model):
    name = models.CharField(null=True, blank=True, max_length=80)
    slug = models.SlugField(max_length=200, default='', null=True, blank=True)
    color = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            value = self.name
            self.slug = slugify(value, allow_unicode=True)
        super(VehicleType, self).save(*args, **kwargs)

class Vehicle(TimeStampMixin):
    name = models.CharField(null=True, blank=True, max_length=80)
    code = models.CharField(null=True, blank=True, max_length=255)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, null=True)
    vehicle_number = models.CharField(null=True, blank=True, max_length=80)
    image = models.ImageField(upload_to='images/vehicle/', null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, null=True, blank=True, max_length=40)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class VehicleAttendance(models.Model):
    date = HStoreField(null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True)