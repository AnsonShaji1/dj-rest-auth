from django.db import models
from django.utils.text import slugify
from dispatch.models import TimeStampMixin

STATUS_CHOICES = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('deleted', 'Deleted')
)

STACK_CHOICE = (
    ('04x03m', '04x03 M'),
)



class StackType(models.Model):
    name = models.CharField(null=True, blank=True, max_length=80)
    slug = models.SlugField(max_length=200, default='', null=True, blank=True)
    color = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            value = self.name
            self.slug = slugify(value, allow_unicode=True)
        super(StackType, self).save(*args, **kwargs)


class Stack(TimeStampMixin):
    code = models.CharField(null=True, blank=True, max_length=255)
    # stack_type = models.CharField(choices=STACK_CHOICE, null=True, blank=True, max_length=40)
    stack_type = models.ForeignKey(StackType, on_delete=models.CASCADE, null=True)
    stack_number = models.CharField(null=True, blank=True, max_length=80)
    quantity = models.FloatField(null=True, blank=True)
    image = models.ImageField(upload_to='images/stack/', null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, null=True, blank=True, max_length=40)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.code