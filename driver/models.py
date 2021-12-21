from django.db import models
from django.utils.text import slugify
from dispatch.models import TimeStampMixin

DRIVER_TYPE = (
    ('inhouse', 'In house'),
    ('outsourced', 'Outsourced')
)

STATUS_CHOICES = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('deleted', 'Deleted')
)


class DriverType(models.Model):
    name = models.CharField(null=True, blank=True, max_length=80)
    slug = models.SlugField(max_length=200, default='', null=True, blank=True)
    color = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            value = self.name
            self.slug = slugify(value, allow_unicode=True)
        super(DriverType, self).save(*args, **kwargs)


class Driver(TimeStampMixin):
    name = models.CharField(null=True, blank=True, max_length=80)
    employee_code = models.CharField(null=True, blank=True, max_length=255)
    driver_type = models.ForeignKey(DriverType, on_delete=models.CASCADE, null=True)
    hour = models.TimeField(null=True, blank=True)
    image = models.ImageField(upload_to='images/driver/', null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, null=True, blank=True, max_length=40)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


from django.contrib.postgres.fields import HStoreField
class DriverAttendance(models.Model):
    date = HStoreField(null=True, blank=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True)