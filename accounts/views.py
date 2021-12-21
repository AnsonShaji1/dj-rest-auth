from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

from .models import User, UserRole
from planner.http import HttpHandler
from rest_framework import status
from .serializers import UserSerializer, UserRoleSerializer
from dispatch.models import StackStatus, Dispatch, DelayReason
from dispatch.serializers import StackStatusSerializer, DispatchSerializer, DelayReasonSerializer
from driver.models import DriverType
from driver.serializers import DriverTypeSerializer
from stack.models import StackType
from stack.serializers import StackTypeSerializer 
from vehicle.models import VehicleType
from vehicle.serializers import VehicleTypeSerializer
from .utils import *

class AccountsView(APIView):
    
    def get(self, request, *args, **kwargs):
        queryset = User.objects.filter(is_superuser=False)
        serializer = UserSerializer(queryset, many=True)
        
        return HttpHandler.json_response_wrapper(
                    [{'response': serializer.data}], 'Successfull', status.HTTP_200_OK,True
                    )

              
    def put(self, request, *args, **kwargs):
        """
        update the user information
        """
        user = User.objects.get(username=request.data['username'])
        user.employee_code = request.data['employee_code']
        user.employee_role = UserRole.objects.get(id=int(request.data['employee_role']))
        user.status = request.data['status']
        user.first_name = request.data['first_name']
        user.save()
        return HttpHandler.json_response_wrapper(
                    [{'response': 'User is updated'}], 'Successfull', status.HTTP_200_OK,True
                    )


    def delete(self, request, *args, **kwargs):
        user = User.objects.get(id=int(kwargs['pk']))
        user.delete()
        return HttpHandler.json_response_wrapper(
                    [{'response': 'Delete user successfully'}], 'Successfull', status.HTTP_200_OK,True
                    )

        


class RoleTypeView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = UserRole.objects.all()
        serializer = UserRoleSerializer(queryset, many=True)
        
        return HttpHandler.json_response_wrapper(
                    [{'response': serializer.data}], 'Successfull', status.HTTP_200_OK,True
                    )



class CommonSettingView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            if data['main_type'] == 'user':
                if data['sub_type'] == 'user_role':
                    user_list = UserRole.objects.filter(name=request.data['name'])
                    if len(user_list) == 0:
                        user_role_settings(data)
                    else:
                        return HttpHandler.json_response_wrapper(
                            [{'response': {'message': "User role already exist"
                            , 'status': False}}
                            ], 'Failed', 400
                        )

            elif data['main_type'] == 'dispatch':

                if data['sub_type'] == 'stack_status':

                    stack_list = StackStatus.objects.filter(name=request.data['name'])
                    if len(stack_list) == 0:
                        dispatch_stack_settings(data)
                    else:
                        return HttpHandler.json_response_wrapper(
                            [{'response': {'message': "Stack status already exist"
                            , 'status': False}}
                            ], 'Failed', 400
                        )

                elif data['sub_type'] == 'delay_reason':

                    delay_list = DelayReason.objects.filter(name=request.data['name'])
                    if len(delay_list) == 0:
                        delay_reason_settings(data)
                    else:
                        return HttpHandler.json_response_wrapper(
                            [{'response': {'message': "Delay reason already exist"
                            , 'status': False}}
                            ], 'Failed', 400
                        )
            
            elif data['main_type'] == 'driver':

                if data['sub_type'] == 'driver_type':
                    driver_list = DriverType.objects.filter(name=request.data['name'])
                    if len(driver_list) == 0:
                        drivertype_settings(data)
                    else:
                        return HttpHandler.json_response_wrapper(
                            [{'response': {'message': "Driver type already exist"
                            , 'status': False}}
                            ], 'Failed', 400
                        )
                
            elif data['main_type'] == 'stack':
                
                if data['sub_type'] == 'stack_type':
                    stack_type_list = StackType.objects.filter(name=request.data['name'])
                    if len(stack_type_list) == 0:
                        stacktype_settings(data)
                    else:
                        return HttpHandler.json_response_wrapper(
                            [{'response': {'message': "Stack type already exist"
                            , 'status': False}}
                            ], 'Failed', 400
                        )
            
            elif data['main_type'] == 'vehicle':
                
                if data['sub_type'] == 'vehicle_type':
                    vehicle_type_list = VehicleType.objects.filter(name=request.data['name'])
                    if len(vehicle_type_list) == 0:
                        vehicletype_settings(data)
                    else:
                        return HttpHandler.json_response_wrapper(
                            [{'response': {'message': "Vehicle type already exist"
                            , 'status': False}}
                            ], 'Failed', 400
                        )

            return HttpHandler.json_response_wrapper(
                        [{'response': {'message': 'Successfull', 'status': True}}], 'Successfull', status.HTTP_200_OK,True
                        )
        except:
            return HttpHandler.json_response_wrapper(
                        [{'response': {'message': 'Something went wrong!', 'status': False}}], 'Successfull', status.HTTP_200_OK,True
                        )


class SettingsView(APIView):
    def get(self, request, *args, **kwargs):
        result = []
        data = {}

        user_role = UserRole.objects.all()
        if len(user_role) > 0 :
            data['parent_slug'] = 'user'
            user_role_serializer = UserRoleSerializer(user_role, many=True)
            data['name'] = 'User Role'
            data['value'] = user_role_serializer.data
            data['slug'] = 'user_role'
            data['depth'] = 2
            result.append(data)
            data = {
                'depth': 1, 'name': 'User', 'slug': 'user'
            }
            result.append(data)
            data = {}

        stack_status = StackStatus.objects.all()
        if len(stack_status) > 0:
            data['parent_slug'] = 'dispatch'
            stack_status_serializer = StackStatusSerializer(stack_status, many=True)
            data['name'] = 'Stack status'
            data['slug'] = 'stack_status'
            data['value'] = stack_status_serializer.data
            data['depth'] = 2
            result.append(data)
            data = {
                'depth': 1, 'name': 'Dispatch', 'slug': 'dispatch'
            }
            result.append(data)
            data = {}
        
        reasons = DelayReason.objects.all()
        if len(reasons) > 0:
            data['parent_slug'] = 'dispatch'
            delay_reason_serializer = DelayReasonSerializer(reasons, many=True)
            data['name'] = 'Delay reason'
            data['slug'] = 'delay_reason'
            data['value'] = delay_reason_serializer.data
            data['depth'] = 2
            result.append(data)
            # data = {
            #     'depth': 1, 'name': 'Dispatch', 'slug': 'dispatch'
            # }
            # result.append(data)
            data = {}

        driver_type = DriverType.objects.all()
        if len(driver_type) > 0:
            data['parent_slug'] = 'driver'
            driver_type_serializer = DriverTypeSerializer(driver_type, many=True)
            data['name'] = 'Driver type'
            data['slug'] = 'driver_type'
            data['depth'] = 2
            data['value'] = driver_type_serializer.data
            result.append(data)
            data = {
                'depth': 1, 'name': 'Driver', 'slug': 'driver'
            }
            result.append(data)
            data = {}
        
        stack_type = StackType.objects.all()
        if len(stack_type) > 0:
            data['parent_slug'] = 'stack'
            stack_type_serializer = StackTypeSerializer(stack_type, many=True)
            data['name'] = 'Stack type'
            data['value'] = stack_type_serializer.data
            data['slug'] = 'stack_type'
            data['depth'] = 2
            result.append(data)
            data = {
                'depth': 1, 'name': 'Stack', 'slug': 'stack'
            }
            result.append(data)
            data = {}
            

        vehicle_type = VehicleType.objects.all()
        if len(vehicle_type) > 0:
            data['parent_slug'] = 'vehicle'
            vehicle_type_serializer = VehicleTypeSerializer(vehicle_type, many=True)
            data['name'] = 'Vehicle type'
            data['value'] = vehicle_type_serializer.data
            data['depth'] = 2
            data['slug'] = 'vehicle_type'
            result.append(data)
            data = {
                'depth': 1, 'name': 'Vehicle', 'slug': 'vehicle'
            }
            result.append(data)
            data = {}

        return HttpHandler.json_response_wrapper(
                    [{'response': result}], 'Successfull', status.HTTP_200_OK,True
                    )