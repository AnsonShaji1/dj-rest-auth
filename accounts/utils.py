from .models import User, UserRole
from dispatch.models import StackStatus, DelayReason
from driver.models import DriverType
from stack.models import StackType
from vehicle.models import VehicleType



def user_role_settings(data):
    if 'id' in data:
        userrole = UserRole.objects.get(id=data['id'])
        userrole.name = data['name']
        if 'color' in data:
            if data['color'] != None:
                userrole.color = data['color']
        userrole.save()
    else:
        if 'color' in data:
            if data['color'] != None:
                userrole = UserRole.objects.create(name=data['name'], color=data['color'])
            else:
               userrole = UserRole.objects.create(name=data['name']) 
        else:
            userrole = UserRole.objects.create(name=data['name'])
        userrole.save()

def dispatch_stack_settings(data):
    if 'id' in data:
        stack = StackStatus.objects.get(id=data['id'])
        stack.name = data['name']
        if 'color' in data:
            if data['color'] != None:
                stack.color = data['color']
    else:
        if 'color' in data:
            if data['color'] != None:
                stack = StackStatus.objects.create(name=data['name'], color=data['color'])
            else:
                stack = StackStatus.objects.create(name=data['name'])
        else:
            stack = StackStatus.objects.create(name=data['name'])
    stack.save()

def delay_reason_settings(data):
    if 'id' in data:
        reason = DelayReason.objects.get(id=data['id'])
        reason.name = data['name']
        if 'color' in data:
            if data['color'] != None:
                reason.color = data['color']
    else:
        if 'color' in data:
            if data['color'] != None:
                reason = DelayReason.objects.create(name=data['name'], color=data['color'])
            else:
                reason = DelayReason.objects.create(name=data['name'])
        else:
            reason = DelayReason.objects.create(name=data['name'])
    reason.save()


def drivertype_settings(data):
    if 'id' in data:
        driver_type = DriverType.objects.get(id=data['id'])
        driver_type.name = data['name']
        if 'color' in data:
            if data['color'] != None:
                driver_type.color = data['color']
    else:
        if 'color' in data:
            if data['color'] != None:
                driver_type = DriverType.objects.create(name=data['name'], color=data['color'])
            else:
                driver_type = DriverType.objects.create(name=data['name'])
        else:
            driver_type = DriverType.objects.create(name=data['name'])
    driver_type.save()


def stacktype_settings(data):
    if 'id' in data:
        stack_type = StackType.objects.get(id=data['id'])
        stack_type.name = data['name']
        if 'color' in data:
            if data['color'] != None:
                stack_type.color = data['color']
    else:
        if 'color' in data:
            if data['color'] != None:
                stack_type = StackType.objects.create(name=data['name'], color=data['color'])
            else:
                stack_type = StackType.objects.create(name=data['name'])
        else:
            stack_type = StackType.objects.create(name=data['name'])
    stack_type.save()


def vehicletype_settings(data):
    if 'id' in data:
        vehicle_type = VehicleType.objects.get(id=data['id'])
        vehicle_type.name = data['name']
        if 'color' in data:
            if data['color'] != None:
                vehicle_type.color = data['color']
    else:
        if 'color' in data:
            if data['color'] != None:
                vehicle_type = VehicleType.objects.create(name=data['name'], color=data['color'])
            else:
                vehicle_type = VehicleType.objects.create(name=data['name'])
        else:
            vehicle_type = VehicleType.objects.create(name=data['name'])
    vehicle_type.save()


