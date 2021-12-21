from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from .serializers import VehicleSerializer, VehicleTypeSerializer
from .models import Vehicle, VehicleType, VehicleAttendance
from planner.http import HttpHandler
from rest_framework import status
from rest_framework import generics

from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin

import datetime
import calendar

from dispatch.models import Dispatch
from django.db.models import Q


class VehicleView(APIView):

    def get(self, request, *args, **kwargs):
        vehicle = Vehicle.objects.get(id=int(self.kwargs['pk']))
        serializer = VehicleSerializer(vehicle)

        return HttpHandler.json_response_wrapper(
                    [{'response': serializer.data}], 'Successfull', status.HTTP_200_OK,True
                    ) 

    def post(self, request, *args, **kwargs):
        data = request.data     
        vehicle_number_list = Vehicle.objects.filter(vehicle_number=request.data['vehicle_number']).exclude(status='deleted')
        if len(vehicle_number_list)==0:
            serializer = VehicleSerializer(data=data)
            if serializer.is_valid():
                serializer.save(user=request.user)
            else:
                return HttpHandler.json_response_wrapper(
                        [{'response': serializer.errors}], 'Failed', 400
                        )
        else:
            return HttpHandler.json_response_wrapper(
                [{'response': {'message': "Vehicle number already exist"
                , 'status': False}}
                 ], 'Failed', 400
            )

        return HttpHandler.json_response_wrapper(
                    [{'response': serializer.data}], 'Successfull', status.HTTP_200_OK,True
                    )


    def delete(self, request, *args, **kwargs):
        vehicle = Vehicle.objects.get(id=int(kwargs['pk']))
        dispatch_list = Dispatch.objects.filter(vehicle__id=vehicle.id).exclude(
            Q(status__slug='deleted') | Q(status__slug='completed'))
        if len(dispatch_list) != 0:
            return HttpHandler.json_response_wrapper(
                [{'response': {'message': "You can't delete the selected vehicle, Since the vehicle is associated with an active dispatch."
                , 'status': False}}
                 ], 'Successfull', status.HTTP_200_OK, True
            )
        else:
            vehicle.status = 'deleted'
            vehicle.save()
            return HttpHandler.json_response_wrapper(
                        [{'response': {'message': 'Vehicle deleted sucessfully', 'status': True}}], 'Successfull', status.HTTP_200_OK,True
                        )


class VehicleTypeList(generics.ListAPIView):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = VehicleTypeSerializer(queryset, many=True)
        return HttpHandler.json_response_wrapper(
                    [{'response': serializer.data}], 'Successfull', status.HTTP_200_OK,True
                    )


class VehicleList(generics.ListAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset().exclude(status='deleted').order_by('-updated_at')
        serializer = VehicleSerializer(queryset, many=True)
        return HttpHandler.json_response_wrapper(
                    [{'response': serializer.data}], 'Successfull', status.HTTP_200_OK,True
                    )


class VehicleUpdate(GenericAPIView, UpdateModelMixin):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    # def put(self, request, *args, **kwargs):
    #     serializer = self.update(request, *args, **kwargs)

    #     return HttpHandler.json_response_wrapper(
    #                 [{'response': serializer.data}], 'Successfull', status.HTTP_200_OK,True
    #                 )

    def put(self, request, *args, **kwargs):
        data = request.data
        if (data['status']):
            if data['status'] == 'inactive':
                vehicle_obj = self.get_object()
                dispatch_list = Dispatch.objects.filter(vehicle__id=vehicle_obj.id).exclude(
                    Q(status__slug='deleted') | Q(status__slug='completed'))
                if len(dispatch_list) != 0:
                    return HttpHandler.json_response_wrapper(
                        [{'response': {'message': "You can't inactive the selected vehicle since the vehicle is associated with an active dispatch"
                        , 'status': False}}
                        ], 'Successfull', status.HTTP_200_OK, True
                    )
                else:               
                    serializer = self.update(request, *args, **kwargs)
                    return HttpHandler.json_response_wrapper(
                        [{'response': {'message': 'Vehicle updated successfully!', 'status': True}}], 'Successfull', status.HTTP_200_OK, True
                    )
            else:
                serializer = self.update(request, *args, **kwargs)
                return HttpHandler.json_response_wrapper(
                    [{'response': {'message': 'Vehicle updated successfully!', 'status': True}}], 'Successfull', status.HTTP_200_OK, True
                )



class AttendanceView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        from_date = datetime.datetime.fromtimestamp(
            int(data['from_date'])/1000.0)

        if 'to_date' in data:
            to_date = datetime.datetime.fromtimestamp(
                int(data['to_date'])/1000.0)

        if data['status'] == 'false':
            dispatch_list = Dispatch.objects.filter(vehicle__id=data['vehicle_id'], date__range=(
                from_date, to_date)).exclude(Q(status__slug='deleted') | Q(status__slug='completed'))
            if len(dispatch_list) != 0:
                return HttpHandler.json_response_wrapper(
                    [{'response': {'message': "You can't change the selected vehicle status, Since the vehicle is associated with an active dispatch", 'status': False}}
                     ], 'Successfull', status.HTTP_200_OK, True
                )
            else:
                pass

        vehicle_exist = VehicleAttendance.objects.filter(
            vehicle__id=data['vehicle_id'])
        if len(vehicle_exist) > 0:
            vehicle_attendance = vehicle_exist[0]
            if to_date:
                diff_days = (to_date - from_date).days + 1
                days = [str((from_date + datetime.timedelta(days=i)).date())
                        for i in range(0, diff_days)]
                for day in days:
                    vehicle_attendance.date[day] = data['status']
                vehicle_attendance.save()
            else:
                vehicle_attendance.date[str(from_date.date())] = data['status']
                vehicle_attendance.save()
        else:
            vehicle = Vehicle.objects.get(id=int(data['vehicle_id']))
            vehicle_attendance = VehicleAttendance.objects.create(
                vehicle=vehicle, date={str(from_date.date()): data['status']})
            if to_date:
                diff_days = (to_date - from_date).days + 1
                days = [str((from_date + datetime.timedelta(days=i)).date())
                        for i in range(0, diff_days)]
                for day in days:
                    vehicle_attendance.date[day] = data['status']
                vehicle_attendance.save()

        return HttpHandler.json_response_wrapper(
            [{'response': {'message':'Vehicle status updated', 'status': True}}
             ], 'Successfull', status.HTTP_200_OK, True
        )


class AttendanceListView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        current_date = datetime.datetime.fromtimestamp(
            int(data['current_date'])/1000.0)

        if current_date.weekday() == 5:
            sat = current_date
        else:
            idx = (current_date.weekday() + 1) % 7
            sat = current_date - datetime.timedelta(7+idx-6)

        year = sat.year
        month = sat.month
        num_days = calendar.monthrange(year, month)[1]
        days = [str(datetime.date(year, month, day))
                for day in range(1, num_days+1)]

        vehicle_list = Vehicle.objects.exclude(Q(status='deleted') | Q(status='inactive'))
        result = []
        keys = [str((sat + datetime.timedelta(days=i)).date())
                for i in range(0, 7)]

        format_keys = [(sat + datetime.timedelta(days=i)).strftime('%d') + ', ' + (sat + datetime.timedelta(days=i)).strftime('%a')
                       for i in range(0, 7)]

        for vehicle in vehicle_list:
            d_dict = {}
            d_dict['name'] = vehicle.name
            att_marked = VehicleAttendance.objects.filter(vehicle__id=vehicle.id)
            if len(att_marked) != 0:
                att_marked = att_marked[0]
                total_leave = len(
                    [day for day in days if day in att_marked.date and att_marked.date[day] == 'false'])
                d_dict['leave'] = total_leave
                for key in keys:
                    if key in att_marked.date:
                        if att_marked.date[key] == 'false':
                            d_dict[key] = 'false'
                        elif att_marked.date[key] == 'true':
                            d_dict[key] = 'true'
                    else:
                        d_dict[key] = 'true'
            else:
                d_dict['leave'] = 0
                for key in keys:
                    d_dict[key] = 'true'
            result.append(d_dict)

        display_date = keys[0].split('-')
        display_month = datetime.datetime(
            int(display_date[0]), int(display_date[1]), int(display_date[2])).strftime('%B')

        return HttpHandler.json_response_wrapper(
            [{'response': result, 'days': keys, 'format_days': format_keys, 'month': display_month}
             ], 'Successfull', status.HTTP_200_OK, True
        )

