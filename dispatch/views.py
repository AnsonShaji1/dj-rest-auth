from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from .serializers import DispatchSerializer, DispatchProjectSerializer, DispatchStackSerializer, \
    DispatchVehicleSerializer, DispatchDriverSerializer, StackStatusSerializer, DispatchTimePlotSerializer, \
    NestedStackSerializer, DelayReasonSerializer, DispatchStatusSerializer
from .models import Dispatch, StackStatus, DispatchStack, DispatchStatus, DelayReason
from planner.http import HttpHandler
from rest_framework import status
from rest_framework import generics

from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
import json
from project.models import Project
from vehicle.models import Vehicle, VehicleAttendance
from driver.models import Driver, DriverAttendance
from stack.models import Stack, StackType
from stack.serializers import StackTypeSerializer
import datetime
from django.db.models import Q
from itertools import chain
from rest_framework.pagination import PageNumberPagination



class DispatchView(APIView):

    def get(self, request, *args, **kwargs):
        dispatch = Dispatch.objects.get(id=int(self.kwargs['pk']))
        serializer = DispatchSerializer(dispatch)

        return HttpHandler.json_response_wrapper(
            [{'response': serializer.data}], 'Successfull', status.HTTP_200_OK, True
        )

    def stringToNumber(self, key, value):
        try:
            converted_value = int(value)
        except:
            converted_value = float(value)
        return key, converted_value

    def post(self, request, *args, **kwargs):
        # create and update api
        data = {
            'project': request.data['project'],
            'vehicle': int(request.data['vehicle']),
            'driver': int(request.data['driver']),
            'reference': request.data['reference']
        }
        if 'date' in request.data:
            cal_date = datetime.datetime.fromtimestamp(
                int(request.data['date'])/1000.0)
            data['date'] = cal_date
        else:
            cal_date = Dispatch.objects.get(id=int(request.data['id'])).date

        if 'note' in request.data:
            if request.data['note']:
                if request.data['note'] != 'null':
                    data['note'] = request.data['note']

        if 'start_time' in request.data:
            # data['start_time'] = datetime.datetime.fromtimestamp(int(request.data['start_time'])/1000.0)
            # data['start_time'] = str(data['start_time'].time()).split('.')[0]
            data['start_time'] = request.data['start_time'] + ':00'
            store_date = str(cal_date.date())
            data['start_time'] = datetime.datetime.strptime(
                store_date + ' ' + data['start_time'], "%Y-%m-%d %H:%M:%S")
        if 'approx_time' in request.data:
            # data['approx_time'] = datetime.datetime.fromtimestamp(int(request.data['approx_time'])/1000.0)
            # data['approx_time'] = str(data['approx_time'].time()).split('.')[0]
            data['approx_time'] = request.data['approx_time'] + ':00'
            store_date = str(cal_date.date())
            data['approx_time'] = datetime.datetime.strptime(
                store_date + ' ' + data['approx_time'], "%Y-%m-%d %H:%M:%S")

        stacks = json.loads(request.data['stack'])
        mod_stack = []

        for stack in stacks:
            stack_obj = {
                "stack": int(stack['stack'])
                # "status": int(stack['status'])
            }
            if stack['id']:
                stack_obj['status'] = int(stack['status'])
            else:
                stack_status_id = StackStatus.objects.get(
                    slug='planned').id
                stack_obj['status'] = stack_status_id

            key, value = self.stringToNumber('payload', stack['payload'])
            stack_obj[key] = value

            key, value = self.stringToNumber('weight', stack['weight'])
            stack_obj[key] = value

            key, value = self.stringToNumber(
                'panel_number', stack['panel_number'])
            stack_obj[key] = value

            if stack['id']:
                stack_obj['id'] = stack['id']
            mod_stack.append(stack_obj)

        data['stack'] = mod_stack

        if ('id' in request.data):
            dispatch = Dispatch.objects.get(id=request.data['id'])
            serializer = DispatchSerializer(dispatch, data=data)
        else:
            data['status'] = DispatchStatus.objects.get(slug='planned').id
            serializer = DispatchSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
        else:
            return HttpHandler.json_response_wrapper(
                [{'response': serializer.errors}], 'Failed', 400
            )

        return HttpHandler.json_response_wrapper(
            [{'response': serializer.data}], 'Successfull', status.HTTP_200_OK, True
        )

    def delete(self, request, *args, **kwargs):
        dispatch = Dispatch.objects.get(id=int(kwargs['pk']))
        dispatch.status = DispatchStatus.objects.get(slug='deleted')
        dispatch.save()

        return HttpHandler.json_response_wrapper(
            [{'response': 'Dispatch deleted sucessfully'}
             ], 'Successfull', status.HTTP_200_OK, True
        )

    def stackfilterData(self, request, *args, **kwargs):
        projects = Project.objects.all()
        pro_serializer = DispatchProjectSerializer(projects, many=True)

        stack_status = StackStatus.objects.all()
        stack_status_serializer = StackStatusSerializer(stack_status, many=True)

        stack_type = StackType.objects.all()
        stack_type_serializer = StackTypeSerializer(stack_type, many=True)

        return HttpHandler.json_response_wrapper(
            [{'response': {
                'projects': pro_serializer.data,
                'stack_type': stack_type_serializer.data,
                'stack_status': stack_status_serializer.data
            }}], 'Successfull', status.HTTP_200_OK, True
        )

    def relatedData(self, request, *args, **kwargs):
        projects = Project.objects.filter(status='active')
        pro_serializer = DispatchProjectSerializer(projects, many=True)

        vehicles = Vehicle.objects.filter(status='active')
        date = datetime.datetime.now()
        key = str(date.year) + '-' + str(date.month) + '-' + str(date.day)
        mod_vehicle = []
        for vehicle in vehicles:
            attendence = VehicleAttendance.objects.filter(vehicle=vehicle)
            if (len(attendence) > 0):
                if key in attendence.first().date:
                    if (attendence.first().date[key] == 'true'):
                        mod_vehicle.append(vehicle)
                else:
                    mod_vehicle.append(vehicle)
            else:
                mod_vehicle.append(vehicle)
        vehi_serializer = DispatchVehicleSerializer(mod_vehicle, many=True)

        drivers = Driver.objects.filter(status='active')
        mod_driver = []
        for driver in drivers:
            attendence = DriverAttendance.objects.filter(driver=driver)
            if (len(attendence) > 0):
                if key in attendence.first().date:
                    if (attendence.first().date[key] == 'true'):
                        mod_driver.append(driver)
                else:
                    mod_driver.append(driver)
            else:
                mod_driver.append(driver)
        dri_serializer = DispatchDriverSerializer(mod_driver, many=True)

        stacks = Stack.objects.exclude(Q(status='deleted') | Q(status='inactive'))
        stack_serializer = DispatchStackSerializer(stacks, many=True)

        stack_status = StackStatus.objects.all()
        status_serializer = StackStatusSerializer(stack_status, many=True)

        return HttpHandler.json_response_wrapper(
            [{'response': {
                'projects': pro_serializer.data,
                'vehicles': vehi_serializer.data,
                'drivers': dri_serializer.data,
                'stacks': stack_serializer.data,
                'stack_status': status_serializer.data
            }}], 'Successfull', status.HTTP_200_OK, True
        )

class ActiveCheckView(APIView):
    def post(self, request, *args, **kwargs):

        vehicles = Vehicle.objects.filter(status='active')
        try:
            date = datetime.datetime.fromtimestamp(
                    int(request.data['date'])/1000.0)
        except:
            date = datetime.datetime.now()
        key = str(date.year) + '-' + str(date.month) + '-' + str(date.day)
        mod_vehicle = []
        for vehicle in vehicles:
            attendence = VehicleAttendance.objects.filter(vehicle=vehicle)
            if (len(attendence) > 0):
                if key in attendence.first().date:
                    if (attendence.first().date[key] == 'true'):
                        mod_vehicle.append(vehicle)
                else:
                    mod_vehicle.append(vehicle)
            else:
                mod_vehicle.append(vehicle)
        vehi_serializer = DispatchVehicleSerializer(mod_vehicle, many=True)

        drivers = Driver.objects.filter(status='active')
        mod_driver = []
        for driver in drivers:
            attendence = DriverAttendance.objects.filter(driver=driver)
            if (len(attendence) > 0):
                if key in attendence.first().date:
                    if (attendence.first().date[key] == 'true'):
                        mod_driver.append(driver)
                else:
                    mod_driver.append(driver)
            else:
                mod_driver.append(driver)
        dri_serializer = DispatchDriverSerializer(mod_driver, many=True)

        return HttpHandler.json_response_wrapper(
            [{'response': {
                'vehicles': vehi_serializer.data,
                'drivers': dri_serializer.data
            }}], 'Successfull', status.HTTP_200_OK, True
        )

class setPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'size'

class DispatchList(generics.ListAPIView):
    queryset = Dispatch.objects.all()
    serializer_class = DispatchSerializer
    pagination_class = setPagination

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset().exclude(Q(status__slug='deleted') | Q(status__slug='completed')).order_by('-updated_at')
        queryset = self.paginate_queryset(queryset)
        pageCount = self.paginator.page
        serializer = DispatchSerializer(queryset, many=True)
        return HttpHandler.json_response_wrapper(
            [{'Count':pageCount.paginator.count,'num_pages':pageCount.paginator.num_pages,'response': serializer.data}], 'Successfull', status.HTTP_200_OK, True
        )


class DispatchTimeCheck(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        if 'date' in request.data:
            cal_date = datetime.datetime.fromtimestamp(
                int(request.data['date'])/1000.0)
        else:
            cal_date = Dispatch.objects.get(id=int(request.data['id'])).date

        start_time = request.data['start_time'] + ':00'
        store_date = str(cal_date.date())
        start_time = datetime.datetime.strptime(
            store_date + ' ' + start_time, "%Y-%m-%d %H:%M:%S")
        approx_time = request.data['approx_time'] + ':00'
        approx_time = datetime.datetime.strptime(
            store_date + ' ' + approx_time, "%Y-%m-%d %H:%M:%S")

        if 'id' in data:
            # start_conflict = Dispatch.objects.filter(
            #     start_time__range=(start_time, approx_time)).exclude(id=int(data['id']))

            start_conflict = Dispatch.objects.filter(
                Q(vehicle__id=int(data['vehicle'])) | Q(driver__id=int(data['driver']))).filter(
                    start_time__range=(start_time, approx_time)).exclude(
                    status__slug='deleted').exclude(id=int(data['id']))

            end_conflict = Dispatch.objects.filter(
                Q(vehicle__id=int(data['vehicle'])) | Q(driver__id=int(data['driver']))).filter(
                    approx_time__range=(start_time, approx_time)).exclude(
                    status__slug='deleted').exclude(id=int(data['id']))

            during_conflict = Dispatch.objects.filter(
                Q(vehicle__id=int(data['vehicle'])) | Q(driver__id=int(data['driver']))).filter(
                    start_time__lte=start_time, approx_time__gte=approx_time).exclude(
                    status__slug='deleted').exclude(id=int(data['id']))
        else:
            start_conflict = Dispatch.objects.filter(
                Q(vehicle__id=int(data['vehicle'])) | Q(driver__id=int(data['driver']))).filter(
                    start_time__range=(start_time, approx_time)).exclude(status__slug='deleted')

            end_conflict = Dispatch.objects.filter(
                Q(vehicle__id=int(data['vehicle'])) | Q(driver__id=int(data['driver']))).filter(
                    approx_time__range=(start_time, approx_time)).exclude(
                        status__slug='deleted')

            during_conflict = Dispatch.objects.filter(
                Q(vehicle__id=int(data['vehicle'])) | Q(driver__id=int(data['driver']))).filter(
                    start_time__lte=start_time, approx_time__gte=approx_time).exclude(
                        status__slug='deleted')

        if (start_conflict or end_conflict or during_conflict):
            return HttpHandler.json_response_wrapper(
                [{'response': {'availability': False}}
                 ], 'Successfull', status.HTTP_200_OK, True
            )
        else:
            return HttpHandler.json_response_wrapper(
                [{'response': {'availability': True}}
                 ], 'Successfull', status.HTTP_200_OK, True
            )


class TimePlotView(APIView):
    def post(self, request, *args, **kwargs):

        from_date = datetime.datetime.fromtimestamp(
            int(request.data['from'])/1000.0)

        if request.data['type'] == 'driver':
            # queryset = Dispatch.objects.filter(
            #     start_time__date__gte=datetime.date(from_date.year,from_date.month,from_date.day),
            #     driver__id=int(request.data['id'])
            #     )
            queryset = Dispatch.objects.filter(
                driver__id=int(request.data['id'])).exclude(status__slug='deleted')
        elif request.data['type'] == 'vehicle':
            # queryset = Dispatch.objects.filter(
            #     start_time__date__gte=datetime.date(from_date.year,from_date.month,from_date.day),
            #     vehicle__id=int(request.data['id'])
            #     )
            queryset = Dispatch.objects.filter(
                vehicle__id=int(request.data['id'])).exclude(status__slug='deleted')

        serializer = DispatchTimePlotSerializer(queryset, many=True)

        return HttpHandler.json_response_wrapper(
            [{'response': serializer.data}], 'Successfull', status.HTTP_200_OK, True
        )


class DispatchFilterView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        filter_query_list = []
        if 'driver' in data:
            if data['driver']:
                filter_query_list.append(Q(driver__id=int(data['driver'])))
        if 'project' in data:
            if data['project']:
                filter_query_list.append(Q(project_id=int(data['project'])))
        if 'date' in data:
            if data['date']:
                date = data['date'].split('-')
                filter_query_list.append(Q(date__year=int(date[0])))
                filter_query_list.append(Q(date__month=int(date[1])))
                filter_query_list.append(Q(date__day=int(date[2])))

                if 'from_time' in data:
                    start_time = request.data['from_time'] + ':00'
                    store_date = str(request.data['date'])
                    start_time = datetime.datetime.strptime(
                        store_date + ' ' + start_time, "%Y-%m-%d %H:%M:%S")
                
                if 'to_time' in data:
                    approx_time = request.data['to_time'] + ':00'
                    store_date = str(request.data['date'])
                    approx_time = datetime.datetime.strptime(
                        store_date + ' ' + approx_time, "%Y-%m-%d %H:%M:%S")
        
        if 'vehicle' in data:
            if data['vehicle']:
                filter_query_list.append(Q(vehicle__id=int(data['vehicle'])))
        if 'status' in data:
            if data['status']:
                filter_query_list.append(Q(status__id=int(data['status'])))
        

        filter_qs = Q()
        for filter_query in filter_query_list:
            filter_qs = filter_qs & filter_query

        dispatch_list = Dispatch.objects.filter(filter_qs).exclude(status__slug='deleted')
        paginator =  setStatusPagination()

        if 'date' in data:
            if data['date']:
                if 'from_time' in data and 'to_time' in data:
                    dispatch_list = dispatch_list.filter(start_time__range=(start_time, approx_time))
                elif 'from_time' in data:
                    dispatch_list = dispatch_list.filter(start_time__gte=start_time)
                elif 'to_time' in data:
                    dispatch_list = dispatch_list.filter(approx_time__lte=approx_time)


        result_page = paginator.paginate_queryset(dispatch_list, request)
        pageCount = paginator.page
        serializer = DispatchSerializer(result_page, many=True)
        
        return HttpHandler.json_response_wrapper(
            [{'num_pages':pageCount.paginator.num_pages,'response': serializer.data}], 'Successfull', status.HTTP_200_OK, True
        )

    def relatedData(self, request, *args, **kwargs):
        projects = Project.objects.filter(status='active')
        pro_serializer = DispatchProjectSerializer(projects, many=True)

        vehicles = Vehicle.objects.filter(status='active')
        vehi_serializer = DispatchVehicleSerializer(vehicles, many=True)

        drivers = Driver.objects.filter(status='active')
        dri_serializer = DispatchDriverSerializer(drivers, many=True)

        dispatch_status = DispatchStatus.objects.all()
        status_serializer = DispatchStatusSerializer(dispatch_status, many=True)


        return HttpHandler.json_response_wrapper(
            [{'response': {
                'projects': pro_serializer.data,
                'vehicles': vehi_serializer.data,
                'drivers': dri_serializer.data,
                'status': status_serializer.data
            }}], 'Successfull', status.HTTP_200_OK, True
        )

class setStatusPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'size'

class DispatchStackView(APIView):
    pagination_class = setPagination
    def get(self, request, *args, **kwargs):
        dispatch_ids = Dispatch.objects.exclude(
            Q(status__slug='deleted')).values_list('stack__id', flat=True)
        queryset = DispatchStack.objects.filter(id__in=dispatch_ids).exclude(Q(status__slug='returned'))
        paginator =  setStatusPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        pageCount = paginator.page
        serializer = NestedStackSerializer(result_page, many=True)
        return HttpHandler.json_response_wrapper(
            [{'Count':pageCount.paginator.count,'num_pages':pageCount.paginator.num_pages,'response': serializer.data}], 'Successfull', status.HTTP_200_OK, True
        )

    def get_stack_status(self, request, *args, **kwargs):
        queryset = StackStatus.objects.all()
        serializer = StackStatusSerializer(queryset, many=True)
        return HttpHandler.json_response_wrapper(
            [{'response': serializer.data}], 'Successfull', status.HTTP_200_OK, True
        )
    
    def post(self, request, *args, **kwargs):
        data = request.data
        filter_query_list = []
        if 'dispatch_ref' in data:
            if data['dispatch_ref']:
                filter_query_list.append(Q(code__icontains=data['dispatch_ref']))
        if 'project' in data:
            if data['project']:
                filter_query_list.append(Q(project_id=int(data['project'])))
        if 'date' in data:
            if data['date']:
                date = data['date'].split('-')
                filter_query_list.append(Q(date__year=int(date[0])))
                filter_query_list.append(Q(date__month=int(date[1])))
                filter_query_list.append(Q(date__day=int(date[2])))

        filter_qs = Q()
        for filter_query in filter_query_list:
            filter_qs = filter_qs & filter_query

        dispatch_ids = Dispatch.objects.filter(
            filter_qs).values_list('stack__id', flat=True).exclude(status__slug='deleted')
        queryset = DispatchStack.objects.filter(id__in=dispatch_ids)
        paginator =  setStatusPagination()
        if 'stack_type' in data:
            if data['stack_type']:
                queryset = queryset.filter(stack__stack_type__id=data['stack_type'])
        if 'status' in data:
            if data['status']:
                queryset = queryset.filter(status__id=int(data['status'])).exclude(status__slug='deleted')

        result_page = paginator.paginate_queryset(queryset, request)
        pageCount = paginator.page
        serializer = NestedStackSerializer(result_page, many=True)
        return HttpHandler.json_response_wrapper(
            [{'num_pages':pageCount.paginator.num_pages,'response': serializer.data}], 'Successfull', status.HTTP_200_OK, True
        )


class UpdateStackStatus(APIView):

    def post(self, request, *args, **kwargs):
        stacks = json.loads(request.data['stack'])

        for stack in stacks.items():
            status_id = int(stack[0].split('stack-')[1])
            dispatch_stack = DispatchStack.objects.get(id=status_id)
            dispatch_stack.status = StackStatus.objects.get(id=int(stack[1]))
            dispatch_stack.save()
        return HttpHandler.json_response_wrapper(
            [{'response': 'Successfull'}], 'Successfull', status.HTTP_200_OK, True
        )


class DelayedReasonView(APIView):

    def get(self, request, *args, **kwargs):
        reasons = DelayReason.objects.all()
        serializer = DelayReasonSerializer(reasons, many=True)
        return HttpHandler.json_response_wrapper(
            [{'response': serializer.data}], 'Successfull', status.HTTP_200_OK, True
        )


class UpdateRemarkView(APIView):

    def post(self, request, *args, **kwargs):
        data = request.data
        dispatch = Dispatch.objects.get(id=int(data['id']))

        cal_date = dispatch.date
        data['return_time'] = data['return_time'] + ':00'
        store_date = str(cal_date.date())
        data['return_time'] = datetime.datetime.strptime(
            store_date + ' ' + data['return_time'], "%Y-%m-%d %H:%M:%S")

        dispatch.return_time = data['return_time']
        if 'remarks' in data:
            dispatch.remarks = data['remarks']
        if 'delay_reason' in data:
            dispatch.delay_reason = DelayReason.objects.get(
                id=int(data['delay_reason']))
        dispatch.status = DispatchStatus.objects.get(slug='completed')
        for stack in dispatch.stack.all():
            stack.status = StackStatus.objects.get(slug='deployed')
            stack.save()
        dispatch.save()

        if (data['return_time'] > dispatch.approx_time):
            difference_time = data['return_time'] - dispatch.approx_time

            start_conflict = Dispatch.objects.filter(
                Q(vehicle__id=int(dispatch.vehicle.id)) | Q(driver__id=int(dispatch.driver.id))).filter(
                    start_time__range=(dispatch.start_time, data['return_time'])).exclude(
                    status__slug='deleted').exclude(id=int(dispatch.id))

            end_conflict = Dispatch.objects.filter(
                Q(vehicle__id=int(dispatch.vehicle.id)) | Q(driver__id=int(dispatch.driver.id))).filter(
                    approx_time__range=(dispatch.start_time, data['return_time'])).exclude(
                    status__slug='deleted').exclude(id=int(dispatch.id))

            during_conflict = Dispatch.objects.filter(
                Q(vehicle__id=int(dispatch.vehicle.id)) | Q(driver__id=int(dispatch.driver.id))).filter(
                    start_time__lte=dispatch.start_time, approx_time__gte=data['return_time']).exclude(
                    status__slug='deleted').exclude(id=int(dispatch.id))
            
            if (start_conflict or end_conflict or during_conflict):
                remaining_daily_dispatch = Dispatch.objects.filter(date__year=dispatch.date.year, 
                    date__month=dispatch.date.month, date__day=dispatch.date.day, start_time__gt=dispatch.start_time).exclude(
                    id=dispatch.id).order_by('start_time')

                for i,daily_dispatch in enumerate(remaining_daily_dispatch):
                    if (i == 0):
                        if (data['return_time'] > daily_dispatch.start_time):
                            current_date = datetime.datetime(
                                year=daily_dispatch.date.year,
                                month=daily_dispatch.date.month,
                                day=daily_dispatch.date.day)

                            daily_dispatch.start_time += difference_time
                            mod_startdate = datetime.datetime(
                                year=daily_dispatch.start_time.year,
                                month=daily_dispatch.start_time.month,
                                day=daily_dispatch.start_time.day)
                            if (mod_startdate > current_date):
                                daily_dispatch.start_time = datetime.datetime(
                                    daily_dispatch.date.year, daily_dispatch.date.month, 
                                    daily_dispatch.date.day, 23, 59)


                            daily_dispatch.approx_time += difference_time
                            mod_approdate = datetime.datetime(
                                year=daily_dispatch.approx_time.year,
                                month=daily_dispatch.approx_time.month,
                                day=daily_dispatch.approx_time.day)
                            if (mod_approdate > current_date):
                                daily_dispatch.approx_time = datetime.datetime(
                                    daily_dispatch.date.year, daily_dispatch.date.month, 
                                    daily_dispatch.date.day, 23, 59)
                            daily_dispatch.save()
                        else:
                            return HttpHandler.json_response_wrapper(
                                [{'response': 'Updated dispatch successfull'}
                                ], 'Successfull', status.HTTP_200_OK, True
                            )
                    else:
                        if (remaining_daily_dispatch[i-1].approx_time > daily_dispatch.start_time):
                            daily_dispatch.start_time += difference_time
                            daily_dispatch.approx_time += difference_time
                            daily_dispatch.save()
                        else:
                            return HttpHandler.json_response_wrapper(
                                [{'response': 'Updated dispatch successfull'}
                                ], 'Successfull', status.HTTP_200_OK, True
                            )
            
            print(dispatch.id)

        return HttpHandler.json_response_wrapper(
            [{'response': 'Updated dispatch successfull'}
             ], 'Successfull', status.HTTP_200_OK, True
        )
