from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

from planner.http import HttpHandler
from rest_framework import status
from rest_framework import generics
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
import json
import datetime
import calendar

from dispatch.models import Dispatch
from vehicle.models import Vehicle
from driver.models import Driver
from django.db.models import Sum, Q
from project.models import Project
from functools import reduce
from stack.models import Stack


# Create your views here.
# Create your views here.
class DashboardView(APIView):
    def post(self, request, *args, **kwargs):
        current_date = datetime.datetime.now()
        vehicle_data = {}
        v_deliveries = {}
        driver_data = {}
        dri_deliveries = {}
        project_data = {}
        project_stack = {}
        seconds_in_day = 24 * 60 * 60
        final_data = {}

        ongoing_dispatch = []
        stack_utilization = []
        stand_by_no = 0
        deployed_no = 0
        stack_data = {}

        ongoing_dispatch_list = Dispatch.objects.filter(start_time__lt=datetime.datetime.now()).exclude(
            Q(status__slug='deleted') | Q(status__slug='completed'))
        if len(ongoing_dispatch_list) > 0:
            for ongoing in ongoing_dispatch_list:
                dispatch_obj = {
                    'id': ongoing.id,
                    'driver': ongoing.driver.name,
                    'vehicle_no': ongoing.vehicle.vehicle_number,
                    'reference_no': ongoing.code,
                    'start_at': ongoing.date.date().strftime('%Y-%m-%d')
                }
                ongoing_dispatch.append(dispatch_obj)
        else:
            ongoing_dispatch = []

        final_data['ongoing_dispatch'] = ongoing_dispatch

        # common utilization
        stack_dispatch_list = Dispatch.objects.exclude(
            Q(status__slug='deleted'))
        if len(stack_dispatch_list) > 0:
            for stack_dipatch in stack_dispatch_list:
                stacks = stack_dipatch.stack.all()
                if len(stacks) > 0:
                    for stackitem in stacks:
                        if stackitem.status.slug == 'deployed' or stackitem.status.slug == 'ready-to-collect':
                            if stackitem.stack.code in stack_data:
                                stack_data[str(stackitem.stack.code)] += 1
                            else:
                                stack_data[str(stackitem.stack.code)] = 1

            # stack utilization
            all_stacks = Stack.objects.filter(status='active')
            for stack_item in all_stacks:
                stack_obj = {}
                stack_obj['name'] = stack_item.code
                if stack_item.code in stack_data:
                    stack_obj['deploy'] = stack_data[stack_item.code]
                    stack_obj['standby'] = stack_item.quantity - \
                        float(stack_obj['deploy'])
                else:
                    stack_obj['standby'] = stack_item.quantity
                    stack_obj['deploy'] = 0

                stand_by_no += int(stack_obj['standby'])
                deployed_no += int(stack_obj['deploy'])

                stack_utilization.append(stack_obj)

            total_stack_ut = stand_by_no + deployed_no
            if total_stack_ut != 0:
                if stand_by_no != 0:
                    stand_by_qt = stand_by_no / total_stack_ut
                    standby_pecent = stand_by_qt * 100
                else:
                    standby_pecent = 0
                if deployed_no != 0:
                    deploye_qt = deployed_no / total_stack_ut
                    deploye_pecent = deploye_qt * 100
                else:
                    deploye_pecent = 0
            else:
                standby_pecent = 50.0
                deploye_pecent = 50.0

            final_data['stack'] = {
                'stack_utilization': stack_utilization,
                'stand_by_no': stand_by_no,
                'deployed_no': deployed_no,
                'standby_percent': standby_pecent,
                'deploye_pecent': deploye_pecent
            }

        else:
            all_stacks = Stack.objects.filter(status='active')
            if len(all_stacks) != 0:
                for stack_item in all_stacks:
                    stack_obj = {}
                    stack_obj['name'] = stack_item.code
                    stack_obj['standby'] = stack_item.quantity
                    stack_obj['deploy'] = 0

                    stand_by_no += int(stack_obj['standby'])
                    stack_utilization.append(stack_obj)

                total_stack_ut = stand_by_no + deployed_no
                if total_stack_ut != 0:
                    if stand_by_no != 0:
                        stand_by_qt = stand_by_no / total_stack_ut
                        standby_pecent = stand_by_qt * 100
                    else:
                        standby_pecent = 0
                    if deployed_no != 0:
                        deploye_qt = deployed_no / total_stack_ut
                        deploye_pecent = deploye_qt * 100
                    else:
                        deploye_pecent = 0
                else:
                    standby_pecent = 50.0
                    deploye_pecent = 50.0

                final_data['stack'] = {
                    'stack_utilization': stack_utilization,
                    'stand_by_no': stand_by_no,
                    'deployed_no': deployed_no,
                    'standby_percent': standby_pecent,
                    'deploye_pecent': deploye_pecent
                }

            else:
                final_data['stack'] = {
                    'stack_utilization': [],
                    'stand_by_no': 0,
                    'deployed_no': 0,
                    'standby_percent': 50,
                    'deploye_pecent': 50
                }

        final_vehicle_utilization = []
        vehicle_utilization = {}
        driver_utilization = {}
        final_driver_utilization = []
        project_utilization = []

        all_vehicles = [{vehicle.id: 0}
            for vehicle in Vehicle.objects.filter(status='active')]
        all_drivers = [{driver.id: 0}
            for driver in Driver.objects.filter(status='active')]

        if request.data['filter'] == 'today':
            dispatch_list = Dispatch.objects.filter(date__year=current_date.year,
                date__month=current_date.month, date__day=current_date.day).exclude(
                status__slug='deleted')
            if len(dispatch_list) > 0:
                for dispatch in dispatch_list:
                    difference = dispatch.approx_time - dispatch.start_time
                    # vehicle
                    if dispatch.vehicle.id in vehicle_data:
                        vehicle_data[dispatch.vehicle.id].append(difference)
                    else:
                        vehicle_data[dispatch.vehicle.id] = [difference]

                    if dispatch.vehicle.id in v_deliveries:
                        v_deliveries[dispatch.vehicle.id].append(1)
                    else:
                        v_deliveries[dispatch.vehicle.id] = [1]

                    # driver
                    if dispatch.driver.id in driver_data:
                        driver_data[dispatch.driver.id].append(difference)
                    else:
                        driver_data[dispatch.driver.id] = [difference]
                    if dispatch.driver.id in dri_deliveries:
                        dri_deliveries[dispatch.driver.id].append(1)
                    else:
                        dri_deliveries[dispatch.driver.id] = [1]

                    # project
                    if dispatch.project.id in project_data:
                        project_data[dispatch.project.id].append(
                            dispatch.stack.aggregate(Sum('payload'))['payload__sum'])
                    else:
                        project_data[dispatch.project.id] = [dispatch.stack.aggregate(Sum('payload'))[
                            'payload__sum']]
                    if dispatch.project.id in project_stack:
                        project_stack[dispatch.project.id].append(1)
                    else:
                        project_stack[dispatch.project.id] = [1]

                # calculate vehicle utilization only having dispatches
                for data in vehicle_data.items():
                    obj = {}
                    vehicle = Vehicle.objects.get(id=int(data[0]))
                    obj['id'] = vehicle.id
                    obj['name'] = vehicle.name
                    obj['number'] = vehicle.vehicle_number
                    obj['total_delivery'] = sum(v_deliveries[data[0]])
                    total_time_delta = sum(data[1], datetime.timedelta())
                    value = divmod(total_time_delta.days *
                                   seconds_in_day + total_time_delta.seconds, 60)
                    percentage = (((value[0] * 60) + value[1])
                                  * 100)/seconds_in_day
                    obj['percentage'] = round(percentage)
                    vehicle_utilization[vehicle.id] = obj

                # final calculation of vehicle utilization of all vehicles
                for i in all_vehicles:
                    if list(i.keys())[0] in vehicle_utilization:
                        final_vehicle_utilization.append(
                            vehicle_utilization[list(i.keys())[0]])
                    else:
                        vehicle_id = list(i.keys())[0]
                        obj = {}
                        vehicle = Vehicle.objects.get(id=vehicle_id)
                        obj['id'] = vehicle.id
                        obj['name'] = vehicle.name
                        obj['number'] = vehicle.vehicle_number
                        obj['total_delivery'] = 0
                        obj['percentage'] = 0
                        final_vehicle_utilization.append(obj)

                # calculate driver utilization only having dispatches
                for data in driver_data.items():
                    obj = {}
                    driver = Driver.objects.get(id=int(data[0]))
                    obj['id'] = driver.id
                    obj['name'] = driver.name
                    obj['total_delivery'] = sum(dri_deliveries[data[0]])
                    total_time_delta = sum(data[1], datetime.timedelta())
                    value = divmod(total_time_delta.days *
                                   seconds_in_day + total_time_delta.seconds, 60)
                    # obj['total_time'] = str(value[0]) + ':' + str(value[1])
                    # obj['driver_hour'] = driver.hour
                    percentage = (
                        (((value[0] * 60) + value[1]) * 100)/((driver.hour.hour * 60*60) + (driver.hour.minute * 60)))
                    obj['percentage'] = round(percentage)
                    driver_utilization[driver.id] = obj

                # final calculation of driver utilization of all drivers
                for i in all_drivers:
                    if list(i.keys())[0] in driver_utilization:
                        final_driver_utilization.append(
                            driver_utilization[list(i.keys())[0]])
                    else:
                        driver_id = list(i.keys())[0]
                        obj = {}
                        driver = Driver.objects.get(id=driver_id)
                        obj['id'] = driver.id
                        obj['name'] = driver.name
                        obj['total_delivery'] = 0
                        obj['percentage'] = 0
                        final_driver_utilization.append(obj)

                for data in project_data.items():
                    obj = {}
                    project = Project.objects.get(id=int(data[0]))
                    obj['id'] = project.id
                    obj['name'] = project.name
                    obj['code'] = project.code
                    obj['total_payload'] = sum(data[1])
                    obj['total_deliveries'] = sum(project_stack[data[0]])
                    project_utilization.append(obj)

                if len(project_utilization) > 0:
                    largest_pro = reduce(lambda largest, current: largest if (
                        largest['total_payload'] > current['total_payload']) else current, project_utilization)

                    highest_dispatches = Dispatch.objects.filter(
                        project__id=largest_pro['id']).exclude(status__slug='deleted')

                    individual_pro_payload = 0
                    for i in highest_dispatches:
                        try:
                            individual_pro_payload += i.stack.all().aggregate(Sum('payload')
                                                                              )['payload__sum']
                        except:
                            pass

                    individual_pro = Project.objects.get(id=largest_pro['id'])
                    total_indivi_order = individual_pro.total_order
                    project_percentage = (
                        individual_pro_payload / total_indivi_order) * 100
                else:
                    project_percentage = 0
                    individual_pro_payload = 0

                final_data['vehicle_utilization'] = final_vehicle_utilization
                final_data['driver_utilization'] = final_driver_utilization
                final_data['project'] = {
                    'project_utilization': project_utilization,
                    'data': {
                        'percentage': round(project_percentage),
                        'payload': individual_pro_payload,
                        'name': individual_pro.name
                    }
                }

            else:
                for i in all_vehicles:
                    vehicle_id = list(i.keys())[0]
                    obj = {}
                    vehicle = Vehicle.objects.get(id=vehicle_id)
                    obj['id'] = vehicle.id
                    obj['name'] = vehicle.name
                    obj['number'] = vehicle.vehicle_number
                    obj['total_delivery'] = 0
                    obj['percentage'] = 0
                    final_vehicle_utilization.append(obj)

                for i in all_drivers:
                    driver_id = list(i.keys())[0]
                    obj = {}
                    driver = Driver.objects.get(id=driver_id)
                    obj['id'] = driver.id
                    obj['name'] = driver.name
                    obj['total_delivery'] = 0
                    obj['percentage'] = 0
                    final_driver_utilization.append(obj)

                final_data['vehicle_utilization'] = final_vehicle_utilization
                final_data['driver_utilization'] = final_driver_utilization
                final_data['project'] = {
                    'project_utilization': [],
                    'data': {
                        'percentage': 0,
                        'payload': 0,
                    }
                }

        return HttpHandler.json_response_wrapper(
            [{'response': final_data}], 'Successfull', status.HTTP_200_OK, True
        )


class VehicleUtilizationView(APIView):
    def post(self, request, *args, **kwargs):
        final_vehicle_utilization = []
        vehicle_utilization = {}
        vehicle_data = {}
        v_deliveries = {}
        seconds_in_day = 24 * 60 * 60
        all_vehicles = [{vehicle.id: 0}
            for vehicle in Vehicle.objects.filter(status='active')]
        current_date = datetime.datetime.now()

        if request.data['filter'] == 'today':
            dispatch_list = Dispatch.objects.filter(date__year=current_date.year,
                date__month=current_date.month, date__day=current_date.day).exclude(
                status__slug='deleted')
            if len(dispatch_list) > 0:
                for dispatch in dispatch_list:
                    difference = dispatch.approx_time - dispatch.start_time
                    # vehicle
                    if dispatch.vehicle.id in vehicle_data:
                        vehicle_data[dispatch.vehicle.id].append(difference)
                    else:
                        vehicle_data[dispatch.vehicle.id] = [difference]

                    if dispatch.vehicle.id in v_deliveries:
                        v_deliveries[dispatch.vehicle.id].append(1)
                    else:
                        v_deliveries[dispatch.vehicle.id] = [1]
                # calculate vehicle utilization only having dispatches
                for data in vehicle_data.items():
                    obj = {}
                    vehicle = Vehicle.objects.get(id=int(data[0]))
                    obj['id'] = vehicle.id
                    obj['name'] = vehicle.name
                    obj['number'] = vehicle.vehicle_number
                    obj['total_delivery'] = sum(v_deliveries[data[0]])
                    total_time_delta = sum(data[1], datetime.timedelta())
                    value = divmod(total_time_delta.days *
                                   seconds_in_day + total_time_delta.seconds, 60)
                    percentage = (((value[0] * 60) + value[1])
                                  * 100)/seconds_in_day
                    obj['percentage'] = round(percentage)
                    vehicle_utilization[vehicle.id] = obj

                # final calculation of vehicle utilization of all vehicles
                for i in all_vehicles:
                    if list(i.keys())[0] in vehicle_utilization:
                        final_vehicle_utilization.append(
                            vehicle_utilization[list(i.keys())[0]])
                    else:
                        vehicle_id = list(i.keys())[0]
                        obj = {}
                        vehicle = Vehicle.objects.get(id=vehicle_id)
                        obj['id'] = vehicle.id
                        obj['name'] = vehicle.name
                        obj['number'] = vehicle.vehicle_number
                        obj['total_delivery'] = 0
                        obj['percentage'] = 0
                        final_vehicle_utilization.append(obj)
            else:
                for i in all_vehicles:
                    vehicle_id = list(i.keys())[0]
                    obj = {}
                    vehicle = Vehicle.objects.get(id=vehicle_id)
                    obj['id'] = vehicle.id
                    obj['name'] = vehicle.name
                    obj['number'] = vehicle.vehicle_number
                    obj['total_delivery'] = 0
                    obj['percentage'] = 0
                    final_vehicle_utilization.append(obj)

        elif request.data['filter'] == 'week':
            if current_date.weekday() == 5:
                sat = current_date
            else:
                idx = (current_date.weekday() + 1) % 7
                sat = current_date - datetime.timedelta(7+idx-6)

            friday = current_date + datetime.timedelta(6)
            range_starts = datetime.datetime(sat.year, sat.month, sat.day)
            range_ends = datetime.datetime(
                friday.year, friday.month, friday.day)

            dispatch_list = Dispatch.objects.filter(date__range=[range_starts, range_ends]).exclude(
            status__slug='deleted')
            if len(dispatch_list) > 0:
                for dispatch in dispatch_list:
                    difference = dispatch.approx_time - dispatch.start_time
                    # vehicle
                    if dispatch.vehicle.id in vehicle_data:
                        vehicle_data[dispatch.vehicle.id].append(difference)
                    else:
                        vehicle_data[dispatch.vehicle.id] = [difference]

                    if dispatch.vehicle.id in v_deliveries:
                        v_deliveries[dispatch.vehicle.id].append(1)
                    else:
                        v_deliveries[dispatch.vehicle.id] = [1]
                # calculate vehicle utilization only having dispatches
                for data in vehicle_data.items():
                    obj = {}
                    vehicle = Vehicle.objects.get(id=int(data[0]))
                    obj['id'] = vehicle.id
                    obj['name'] = vehicle.name
                    obj['number'] = vehicle.vehicle_number
                    obj['total_delivery'] = sum(v_deliveries[data[0]])
                    total_time_delta = sum(data[1], datetime.timedelta())
                    value = divmod(total_time_delta.days *
                                   seconds_in_day + total_time_delta.seconds, 60)
                    percentage = (((value[0] * 60) + value[1])
                                  * 100)/(seconds_in_day * 7)
                    obj['percentage'] = round(percentage)
                    vehicle_utilization[vehicle.id] = obj

                # final calculation of vehicle utilization of all vehicles
                for i in all_vehicles:
                    if list(i.keys())[0] in vehicle_utilization:
                        final_vehicle_utilization.append(
                            vehicle_utilization[list(i.keys())[0]])
                    else:
                        vehicle_id = list(i.keys())[0]
                        obj = {}
                        vehicle = Vehicle.objects.get(id=vehicle_id)
                        obj['id'] = vehicle.id
                        obj['name'] = vehicle.name
                        obj['number'] = vehicle.vehicle_number
                        obj['total_delivery'] = 0
                        obj['percentage'] = 0
                        final_vehicle_utilization.append(obj)
            else:
                for i in all_vehicles:
                    vehicle_id = list(i.keys())[0]
                    obj = {}
                    vehicle = Vehicle.objects.get(id=vehicle_id)
                    obj['id'] = vehicle.id
                    obj['name'] = vehicle.name
                    obj['number'] = vehicle.vehicle_number
                    obj['total_delivery'] = 0
                    obj['percentage'] = 0
                    final_vehicle_utilization.append(obj)

        elif request.data['filter'] == 'month':
            number_of_days = calendar.monthrange(
                current_date.year, current_date.month)[1]
            dispatch_list = Dispatch.objects.filter(date__year=current_date.year,
                date__month=current_date.month).exclude(
            status__slug='deleted')
            if len(dispatch_list) > 0:
                for dispatch in dispatch_list:
                    difference = dispatch.approx_time - dispatch.start_time
                    # vehicle
                    if dispatch.vehicle.id in vehicle_data:
                        vehicle_data[dispatch.vehicle.id].append(difference)
                    else:
                        vehicle_data[dispatch.vehicle.id] = [difference]

                    if dispatch.vehicle.id in v_deliveries:
                        v_deliveries[dispatch.vehicle.id].append(1)
                    else:
                        v_deliveries[dispatch.vehicle.id] = [1]
                # calculate vehicle utilization only having dispatches
                for data in vehicle_data.items():
                    obj = {}
                    vehicle = Vehicle.objects.get(id=int(data[0]))
                    obj['id'] = vehicle.id
                    obj['name'] = vehicle.name
                    obj['number'] = vehicle.vehicle_number
                    obj['total_delivery'] = sum(v_deliveries[data[0]])
                    total_time_delta = sum(data[1], datetime.timedelta())
                    value = divmod(total_time_delta.days *
                                   seconds_in_day + total_time_delta.seconds, 60)
                    percentage = (((value[0] * 60) + value[1])
                                  * 100)/(seconds_in_day * number_of_days)
                    obj['percentage'] = round(percentage)
                    vehicle_utilization[vehicle.id] = obj

                # final calculation of vehicle utilization of all vehicles
                for i in all_vehicles:
                    if list(i.keys())[0] in vehicle_utilization:
                        final_vehicle_utilization.append(
                            vehicle_utilization[list(i.keys())[0]])
                    else:
                        vehicle_id = list(i.keys())[0]
                        obj = {}
                        vehicle = Vehicle.objects.get(id=vehicle_id)
                        obj['id'] = vehicle.id
                        obj['name'] = vehicle.name
                        obj['number'] = vehicle.vehicle_number
                        obj['total_delivery'] = 0
                        obj['percentage'] = 0
                        final_vehicle_utilization.append(obj)
            else:
                for i in all_vehicles:
                    vehicle_id = list(i.keys())[0]
                    obj = {}
                    vehicle = Vehicle.objects.get(id=vehicle_id)
                    obj['id'] = vehicle.id
                    obj['name'] = vehicle.name
                    obj['number'] = vehicle.vehicle_number
                    obj['total_delivery'] = 0
                    obj['percentage'] = 0
                    final_vehicle_utilization.append(obj)

        final_data = {}
        final_data['vehicle_utilization'] = final_vehicle_utilization

        return HttpHandler.json_response_wrapper(
            [{'response': final_data}], 'Successfull', status.HTTP_200_OK, True
        )


class DriverUtilizationView(APIView):

    def post(self, request, *args, **kwargs):
        seconds_in_day = 24 * 60 * 60
        current_date = datetime.datetime.now()
        driver_data = {}
        dri_deliveries = {}

        driver_utilization = {}
        final_driver_utilization = []
        all_drivers = [{driver.id: 0}
            for driver in Driver.objects.filter(status='active')]

        if request.data['filter'] == 'today':
            dispatch_list = Dispatch.objects.filter(date__year=current_date.year,
                date__month=current_date.month, date__day=current_date.day).exclude(
                status__slug='deleted')
            if len(dispatch_list) > 0:
                for dispatch in dispatch_list:
                    difference = dispatch.approx_time - dispatch.start_time
                    # driver
                    if dispatch.driver.id in driver_data:
                        driver_data[dispatch.driver.id].append(difference)
                    else:
                        driver_data[dispatch.driver.id] = [difference]
                    if dispatch.driver.id in dri_deliveries:
                        dri_deliveries[dispatch.driver.id].append(1)
                    else:
                        dri_deliveries[dispatch.driver.id] = [1]

                # calculate driver utilization only having dispatches
                for data in driver_data.items():
                    obj = {}
                    driver = Driver.objects.get(id=int(data[0]))
                    obj['id'] = driver.id
                    obj['name'] = driver.name
                    obj['total_delivery'] = sum(dri_deliveries[data[0]])
                    total_time_delta = sum(data[1], datetime.timedelta())
                    value = divmod(total_time_delta.days *
                                   seconds_in_day + total_time_delta.seconds, 60)
                    # obj['total_time'] = str(value[0]) + ':' + str(value[1])
                    # obj['driver_hour'] = driver.hour
                    percentage = (
                        (((value[0] * 60) + value[1]) * 100)/((driver.hour.hour * 60*60) + (driver.hour.minute * 60)))
                    obj['percentage'] = round(percentage)
                    driver_utilization[driver.id] = obj

                # final calculation of driver utilization of all drivers
                for i in all_drivers:
                    if list(i.keys())[0] in driver_utilization:
                        final_driver_utilization.append(
                            driver_utilization[list(i.keys())[0]])
                    else:
                        driver_id = list(i.keys())[0]
                        obj = {}
                        driver = Driver.objects.get(id=driver_id)
                        obj['id'] = driver.id
                        obj['name'] = driver.name
                        obj['total_delivery'] = 0
                        obj['percentage'] = 0
                        final_driver_utilization.append(obj)

            else:
                for i in all_drivers:
                    driver_id = list(i.keys())[0]
                    obj = {}
                    driver = Driver.objects.get(id=driver_id)
                    obj['id'] = driver.id
                    obj['name'] = driver.name
                    obj['total_delivery'] = 0
                    obj['percentage'] = 0
                    final_driver_utilization.append(obj)

        elif request.data['filter'] == 'week':
            if current_date.weekday() == 5:
                sat = current_date
            else:
                idx = (current_date.weekday() + 1) % 7
                sat = current_date - datetime.timedelta(7+idx-6)

            friday = current_date + datetime.timedelta(6)
            range_starts = datetime.datetime(sat.year, sat.month, sat.day)
            range_ends = datetime.datetime(
                friday.year, friday.month, friday.day)

            dispatch_list = Dispatch.objects.filter(date__range=[range_starts, range_ends]).exclude(
            status__slug='deleted')

            if len(dispatch_list) > 0:
                for dispatch in dispatch_list:
                    difference = dispatch.approx_time - dispatch.start_time
                    # driver
                    if dispatch.driver.id in driver_data:
                        driver_data[dispatch.driver.id].append(difference)
                    else:
                        driver_data[dispatch.driver.id] = [difference]
                    if dispatch.driver.id in dri_deliveries:
                        dri_deliveries[dispatch.driver.id].append(1)
                    else:
                        dri_deliveries[dispatch.driver.id] = [1]

                # calculate driver utilization only having dispatches
                for data in driver_data.items():
                    obj = {}
                    driver = Driver.objects.get(id=int(data[0]))
                    obj['id'] = driver.id
                    obj['name'] = driver.name
                    obj['total_delivery'] = sum(dri_deliveries[data[0]])
                    total_time_delta = sum(data[1], datetime.timedelta())
                    value = divmod(total_time_delta.days *
                                   seconds_in_day + total_time_delta.seconds, 60)
                    
                    percentage = (((value[0] * 60) + value[1]) * 100) / (((driver.hour.hour * 60*60) + (driver.hour.minute * 60)) * 7 )

                    obj['percentage']=round(percentage)
                    driver_utilization[driver.id]=obj
                # final calculation of driver utilization of all drivers
                for i in all_drivers:
                    if list(i.keys())[0] in driver_utilization:
                        final_driver_utilization.append(
                            driver_utilization[list(i.keys())[0]])
                    else:
                        driver_id=list(i.keys())[0]
                        obj={}
                        driver=Driver.objects.get(id=driver_id)
                        obj['id']=driver.id
                        obj['name']=driver.name
                        obj['total_delivery']=0
                        obj['percentage']=0
                        final_driver_utilization.append(obj)

            else:
                for i in all_drivers:
                    driver_id=list(i.keys())[0]
                    obj={}
                    driver=Driver.objects.get(id=driver_id)
                    obj['id']=driver.id
                    obj['name']=driver.name
                    obj['total_delivery']=0
                    obj['percentage']=0
                    final_driver_utilization.append(obj)



        elif request.data['filter'] == 'month':
            number_of_days=calendar.monthrange(
                current_date.year, current_date.month)[1]
            dispatch_list=Dispatch.objects.filter(date__year=current_date.year, date__month=current_date.month).exclude(
            status__slug='deleted')

            if len(dispatch_list) > 0:
                for dispatch in dispatch_list:
                    difference=dispatch.approx_time - dispatch.start_time
                    # driver
                    if dispatch.driver.id in driver_data:
                        driver_data[dispatch.driver.id].append(difference)
                    else:
                        driver_data[dispatch.driver.id]=[difference]
                    if dispatch.driver.id in dri_deliveries:
                        dri_deliveries[dispatch.driver.id].append(1)
                    else:
                        dri_deliveries[dispatch.driver.id]=[1]


                # calculate driver utilization only having dispatches
                for data in driver_data.items():
                    obj={}
                    driver=Driver.objects.get(id=int(data[0]))
                    obj['id']=driver.id
                    obj['name']=driver.name
                    obj['total_delivery']=sum(dri_deliveries[data[0]])
                    total_time_delta=sum(data[1], datetime.timedelta())
                    value=divmod(total_time_delta.days *
                                   seconds_in_day + total_time_delta.seconds, 60)

                    percentage = (((value[0] * 60) + value[1]) * 100) / (((driver.hour.hour * 60*60) + (driver.hour.minute * 60)) * number_of_days)

                    obj['percentage']=round(percentage)
                    driver_utilization[driver.id]=obj

                # final calculation of driver utilization of all drivers
                for i in all_drivers:
                    if list(i.keys())[0] in driver_utilization:
                        final_driver_utilization.append(
                            driver_utilization[list(i.keys())[0]])
                    else:
                        driver_id=list(i.keys())[0]
                        obj={}
                        driver=Driver.objects.get(id=driver_id)
                        obj['id']=driver.id
                        obj['name']=driver.name
                        obj['total_delivery']=0
                        obj['percentage']=0
                        final_driver_utilization.append(obj)

            else:
                for i in all_drivers:
                    driver_id=list(i.keys())[0]
                    obj={}
                    driver=Driver.objects.get(id=driver_id)
                    obj['id']=driver.id
                    obj['name']=driver.name
                    obj['total_delivery']=0
                    obj['percentage']=0
                    final_driver_utilization.append(obj)

        final_data={}
        final_data['driver_utilization'] = final_driver_utilization

        return HttpHandler.json_response_wrapper(
            [{'response': final_data}], 'Successfull', status.HTTP_200_OK, True
        )


class DashboardDeliveryView(APIView):

    def post(self, request, *args, **kwargs):
        current_date = datetime.datetime.now()
        project_utilization = []
        project_data = {}
        project_stack = {}
        seconds_in_day = 24 * 60 * 60
        final_data = {}
        if request.data['filter'] == 'today':
            delivery_dispatch_list=Dispatch.objects.filter(date__year=current_date.year,
                                                             date__month=current_date.month, date__day=current_date.day).exclude(
                status__slug='deleted')
            if len(delivery_dispatch_list) != 0:
                for delivery_dispatch in delivery_dispatch_list:
                    difference=delivery_dispatch.approx_time - delivery_dispatch.start_time
                    # project
                    if delivery_dispatch.project.id in project_data:
                        project_data[delivery_dispatch.project.id].append(
                            delivery_dispatch.stack.aggregate(Sum('payload'))['payload__sum'])
                    else:
                        project_data[delivery_dispatch.project.id]=[delivery_dispatch.stack.aggregate(Sum('payload'))[
                            'payload__sum']]

                    if delivery_dispatch.project.id in project_stack:
                        project_stack[delivery_dispatch.project.id].append(1)
                    else:
                        project_stack[delivery_dispatch.project.id]=[1]
                for data in project_data.items():
                    obj={}
                    # data[1] = [i for i in data[1] if i] 
                    project=Project.objects.get(id=int(data[0]))
                    obj['id']=project.id
                    obj['name']=project.name
                    obj['code']=project.code
                    obj['total_payload']=sum(data[1])
                    obj['total_deliveries']=sum(project_stack[data[0]])
                    project_utilization.append(obj)

                if len(project_utilization) > 0:
                    largest_pro=reduce(lambda largest, current: largest if (
                        largest['total_payload'] > current['total_payload']) else current, project_utilization)

                    highest_dispatches=Dispatch.objects.filter(
                        project__id=largest_pro['id']).exclude(status__slug='deleted')

                    individual_pro_payload=0
                    for i in highest_dispatches:
                        try:
                            individual_pro_payload += i.stack.all().aggregate(Sum('payload')
                                                                              )['payload__sum']
                        except:
                            pass

                    individual_pro=Project.objects.get(id=largest_pro['id'])
                    total_indivi_order=individual_pro.total_order
                    project_percentage=(
                        individual_pro_payload / total_indivi_order) * 100
                else:
                    project_percentage=0
                    individual_pro_payload=0
                final_data['project']={
                    'project_utilization': project_utilization,
                    'data': {
                        'percentage': round(project_percentage),
                        'payload': individual_pro_payload,
                        'name': individual_pro.name
                    }
                }
            else:
                final_data['project']={
                    'project_utilization': [],
                    'data': {
                        'percentage': 0,
                        'payload': 0,
                        'name': ''
                    }
                }
        elif request.data['filter'] == 'week':
            if current_date.weekday() == 5:
                sat = current_date
            else:
                idx = (current_date.weekday() + 1) % 7
                sat = current_date - datetime.timedelta(7+idx-6)

            friday = current_date + datetime.timedelta(6)
            range_starts = datetime.datetime(sat.year, sat.month, sat.day)
            range_ends = datetime.datetime(
                friday.year, friday.month, friday.day)

            delivery_dispatch_list = Dispatch.objects.filter(date__range=[range_starts, range_ends]).exclude(
            status__slug='deleted')

            if len(delivery_dispatch_list) != 0:
                for delivery_dispatch in delivery_dispatch_list:
                    difference=delivery_dispatch.approx_time - delivery_dispatch.start_time
                    # project
                    if delivery_dispatch.project.id in project_data:
                        project_data[delivery_dispatch.project.id].append(
                            delivery_dispatch.stack.aggregate(Sum('payload'))['payload__sum'])
                    else:
                        project_data[delivery_dispatch.project.id]=[delivery_dispatch.stack.aggregate(Sum('payload'))[
                            'payload__sum']]

                    if delivery_dispatch.project.id in project_stack:
                        project_stack[delivery_dispatch.project.id].append(1)
                    else:
                        project_stack[delivery_dispatch.project.id]=[1]
                for data in project_data.items():
                    obj={}
                    project=Project.objects.get(id=int(data[0]))
                    obj['id']=project.id
                    obj['name']=project.name
                    obj['code']=project.code
                    obj['total_payload']=sum(filter(None, data[1]))
                    obj['total_deliveries']=sum(project_stack[data[0]])
                    project_utilization.append(obj)

                if len(project_utilization) > 0:
                    largest_pro=reduce(lambda largest, current: largest if (
                        largest['total_payload'] > current['total_payload']) else current, project_utilization)

                    highest_dispatches=Dispatch.objects.filter(
                        project__id=largest_pro['id']).exclude(status__slug='deleted')

                    individual_pro_payload=0
                    for i in highest_dispatches:
                        try:
                            individual_pro_payload += i.stack.all().aggregate(Sum('payload')
                                                                              )['payload__sum']
                        except:
                            pass

                    individual_pro=Project.objects.get(id=largest_pro['id'])
                    total_indivi_order=individual_pro.total_order
                    project_percentage=(
                        individual_pro_payload / total_indivi_order) * 100
                else:
                    project_percentage=0
                    individual_pro_payload=0
                final_data['project']={
                    'project_utilization': project_utilization,
                    'data': {
                        'percentage': round(project_percentage),
                        'payload': individual_pro_payload,
                        'name': individual_pro.name
                    }
                }
            else:
                final_data['project']={
                    'project_utilization': [],
                    'data': {
                        'percentage': 0,
                        'payload': 0,
                        'name': ''
                    }
                }
        elif request.data['filter'] == 'month':
            number_of_days=calendar.monthrange(
                current_date.year, current_date.month)[1]
            delivery_dispatch_list=Dispatch.objects.filter(date__year=current_date.year,
                date__month=current_date.month).exclude(
                status__slug='deleted')
            if len(delivery_dispatch_list) != 0:
                for delivery_dispatch in delivery_dispatch_list:
                    difference=delivery_dispatch.approx_time - delivery_dispatch.start_time
                    # project
                    if delivery_dispatch.project.id in project_data:
                        project_data[delivery_dispatch.project.id].append(
                            delivery_dispatch.stack.aggregate(Sum('payload'))['payload__sum'])
                    else:
                        project_data[delivery_dispatch.project.id]=[delivery_dispatch.stack.aggregate(Sum('payload'))[
                            'payload__sum']]

                    if delivery_dispatch.project.id in project_stack:
                        project_stack[delivery_dispatch.project.id].append(1)
                    else:
                        project_stack[delivery_dispatch.project.id]=[1]
                for data in project_data.items():
                    obj={}
                    project=Project.objects.get(id=int(data[0]))
                    obj['id']=project.id
                    obj['name']=project.name
                    obj['code']=project.code
                    obj['total_payload']=sum(filter(None, data[1]))
                    obj['total_deliveries']=sum(project_stack[data[0]])
                    project_utilization.append(obj)
                if len(project_utilization) > 0:
                    largest_pro=reduce(lambda largest, current: largest if (
                        largest['total_payload'] > current['total_payload']) else current, project_utilization)

                    highest_dispatches=Dispatch.objects.filter(
                        project__id=largest_pro['id']).exclude(status__slug='deleted')

                    individual_pro_payload=0
                    for i in highest_dispatches:
                        try:
                            individual_pro_payload += i.stack.all().aggregate(Sum('payload')
                                                                              )['payload__sum']
                        except:
                            pass
                    individual_pro=Project.objects.get(id=largest_pro['id'])
                    total_indivi_order=individual_pro.total_order
                    project_percentage=(
                        individual_pro_payload / (total_indivi_order)) * 100
                else:
                    project_percentage=0
                    individual_pro_payload=0
                final_data['project']={
                    'project_utilization': project_utilization,
                    'data': {
                        'percentage': round(project_percentage),
                        'payload': individual_pro_payload,
                        'name': individual_pro.name
                    }
                }

            else:
                project_utilization=[]
                final_data['project']={
                    'project_utilization': project_utilization,
                    'data': {
                        'percentage': 0,
                        'payload': 0,
                    }
                }
        return HttpHandler.json_response_wrapper(
            [{'response': final_data}], 'Successfull', status.HTTP_200_OK, True
        )
