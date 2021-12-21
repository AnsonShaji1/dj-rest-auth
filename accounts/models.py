from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.text import slugify
# from rest_framework.authtoken.models import Token
# from django.utils.translation import gettext as _
#from core.models import Item

ROLE_CHOICES = (
    ('dispatch-coordinator', 'Dispatch coordinator'),
    ('admin', 'Admin')
)

STATUS_CHOICES = (
    ('active', 'Active'),
    ('inactive', 'Inactive')
)


class UserRole(models.Model):
    name = models.CharField(null=True, blank=True, max_length=40, unique = True)
    slug = models.SlugField(max_length=200, default='', null=True, blank=True)
    color = models.CharField(null=True, blank=True, max_length=40)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            value = self.name
            self.slug = slugify(value, allow_unicode=True)
        super(UserRole, self).save(*args, **kwargs)

class User(AbstractUser):
    employee_code = models.CharField(null=True, blank=True, max_length=255, unique = True)
    employee_role = models.ForeignKey(UserRole, blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(choices=STATUS_CHOICES, null=True, blank=True, max_length=40)

    def __str__(self):
        return "{}".format(self.username)

