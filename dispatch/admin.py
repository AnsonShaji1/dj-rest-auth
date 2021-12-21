from django.contrib import admin
from .models import DispatchStack, Dispatch, StackStatus, DispatchStatus, DelayReason

admin.site.register(Dispatch)
admin.site.register(DispatchStack)
admin.site.register(StackStatus)
admin.site.register(DispatchStatus)
admin.site.register(DelayReason)
