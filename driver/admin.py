from django.contrib import admin
from .models import Driver, DriverType, DriverAttendance

admin.site.register(Driver)
admin.site.register(DriverType)
admin.site.register(DriverAttendance)