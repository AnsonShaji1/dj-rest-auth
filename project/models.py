from django.db import models
import uuid
from dispatch.models import TimeStampMixin


STATUS_CHOICES = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('deleted', 'Deleted')
)

class Project(TimeStampMixin):
    name = models.CharField(null=True, blank=True, max_length=255)
    code = models.CharField(null=True, blank=True, max_length=255)
    travel_time = models.TimeField(null=True, blank=True)
    total_order = models.FloatField(null=True, blank=True)
    contact_name = models.CharField(null=True, blank=True, max_length=255)
    contact_mob = models.CharField(null=True, blank=True, max_length=40)
    address_line_1 = models.CharField(null=True, blank=True, max_length=255)
    address_line_2 = models.CharField(null=True, blank=True, max_length=255)
    status = models.CharField(choices=STATUS_CHOICES, null=True, blank=True, max_length=40)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True)


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = uuid.uuid4().hex[:9].upper()
        super(Project, self).save(*args, **kwargs)

