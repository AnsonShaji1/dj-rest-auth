from django.contrib import admin
from .models import User, UserRole

admin.site.register(User)
admin.site.register(UserRole)
