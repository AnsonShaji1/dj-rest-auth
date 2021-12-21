from django.contrib import admin
from .models import Vehicle, VehicleType, VehicleAttendance

admin.site.register(Vehicle)
admin.site.register(VehicleType)
admin.site.register(VehicleAttendance)
