from django.db import models
from django.utils.text import slugify
from django.db.models import signals
from django.dispatch import receiver
import uuid


STATUS_CHOICES = (
    ('active', 'Active'),
    ('inactive', 'Inactive')
)

class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DispatchStatus(models.Model):
    name = models.CharField(null=True, blank=True, max_length=40, unique = True)
    slug = models.SlugField(max_length=200, default='', null=True, blank=True)
    color = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            value = self.name
            self.slug = slugify(value, allow_unicode=True)
        super(DispatchStatus, self).save(*args, **kwargs)


class DelayReason(models.Model):
    name = models.CharField(null=True, blank=True, max_length=40, unique = True)
    slug = models.SlugField(max_length=200, default='', null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            value = self.name
            self.slug = slugify(value, allow_unicode=True)
        super(DelayReason, self).save(*args, **kwargs)




class StackStatus(models.Model):
    name = models.CharField(null=True, blank=True, max_length=40, unique = True)
    slug = models.SlugField(max_length=200, default='', null=True, blank=True)
    color = models.CharField(null=True, blank=True, max_length=40)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            value = self.name
            self.slug = slugify(value, allow_unicode=True)
        super(StackStatus, self).save(*args, **kwargs)

class DispatchStack(TimeStampMixin):
    # stack_type = models.CharField(choices=STACK_CHOICE, null=True, blank=True, max_length=40)
    stack = models.ForeignKey('stack.Stack', on_delete=models.CASCADE, null=True)
    payload = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    panel_number = models.FloatField(null=True, blank=True)
    status = models.ForeignKey(StackStatus, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return self.stack.code

class Dispatch(TimeStampMixin):
    project = models.ForeignKey('project.Project', on_delete=models.CASCADE, null=True)
    vehicle = models.ForeignKey('vehicle.Vehicle', on_delete=models.CASCADE, null=True)
    driver = models.ForeignKey('driver.Driver', on_delete=models.CASCADE, null=True)
    date = models.DateTimeField(null=True,blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    approx_time = models.DateTimeField(null=True, blank=True)
    reference = models.CharField(null=True, blank=True, max_length=255)
    stack = models.ManyToManyField(DispatchStack)
    status = models.ForeignKey(DispatchStatus, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True)
    code = models.CharField(null=True, blank=True, max_length=255)
    return_time = models.DateTimeField(null=True, blank=True)
    delay_reason = models.ForeignKey(DelayReason, on_delete=models.CASCADE, null=True, blank=True)
    optional_reason = models.CharField(null=True, blank=True, max_length=255)
    remarks = models.TextField(null=True, blank=True, default='')
    note = models.TextField(null=True, blank=True, default='')

    def __str__(self):
        return self.reference
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = uuid.uuid4().hex[:9].upper()
        super(Dispatch, self).save(*args, **kwargs)


@receiver(models.signals.pre_delete, sender=Dispatch)
def delete_dispatch_stack(sender, instance, *args, **kwargs):
    instance.stack.all().delete()

