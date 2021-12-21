from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from .serializers import ProjectSerializer
from .models import Project
from planner.http import HttpHandler
from rest_framework import status
from rest_framework import generics

from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
import datetime
from dispatch.models import Dispatch
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination


class ProjectView(APIView):

    def get(self, request, *args, **kwargs):
        project = Project.objects.get(id=int(self.kwargs['project_id']))
        serializer = ProjectSerializer(project)

        return HttpHandler.json_response_wrapper(
            [{'response': serializer.data}], 'Successfull', status.HTTP_200_OK, True
        )

    def post(self, request, *args, **kwargs):
        data = request.data
        data['travel_time'] = datetime.time(
            int(data['travel_time'].split(':')[0]), int(
                data['travel_time'].split(':')[1])
        )
        project_list = Project.objects.filter(name=request.data['name']).exclude(status='deleted')
        serializer = ProjectSerializer(data=data)
        if len(project_list) == 0:
            if serializer.is_valid():
                serializer.save(user=request.user)
            else:
                return HttpHandler.json_response_wrapper(
                    [{'response': serializer.errors}], 'Failed', 400
                )
        else:
            return HttpHandler.json_response_wrapper(
                [{'response': {'message': "Project name already exist"
                , 'status': False}}
                 ], 'Failed', 400
            )


        return HttpHandler.json_response_wrapper(
            [{'response': serializer.data}], 'Successfull', status.HTTP_200_OK, True
        )

    def delete(self, request, *args, **kwargs):
        project = Project.objects.get(id=int(kwargs['project_id']))
        dispatch_list = Dispatch.objects.filter(project__id=project.id).exclude(
            Q(status__slug='deleted') | Q(status__slug='completed'))
        if len(dispatch_list) != 0:
            return HttpHandler.json_response_wrapper(
                [{'response': {'message': "You can't delete the selected project, Since the project is associated with an active dispatch."
                , 'status': False}}
                 ], 'Successfull', status.HTTP_200_OK, True
            )
        else:
            project.status = 'deleted'
            project.save()
            return HttpHandler.json_response_wrapper(
                [{'response': {'message':'Project deleted sucessfully', 'status': True}}
                ], 'Successfull', status.HTTP_200_OK, True
            )

class setPagination(PageNumberPagination):
    page_size = 10

class ProjectList(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = setPagination

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset().exclude(status='deleted').order_by('-updated_at')
        queryset = self.paginate_queryset(queryset)
        pageCount = self.paginator.page
        serializer = ProjectSerializer(queryset, many=True)
        return HttpHandler.json_response_wrapper(
            [{'num_pages':pageCount.paginator.num_pages,'response': serializer.data}], 'Successfull', status.HTTP_200_OK, True
        )


class ProjectUpdate(GenericAPIView, UpdateModelMixin):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def put(self, request, *args, **kwargs):
        data = request.data
        if (data['status']):
            if data['status'] == 'inactive':
                project_obj = self.get_object()
                dispatch_list = Dispatch.objects.filter(project__id=project_obj.id).exclude(
                    Q(status__slug='deleted') | Q(status__slug='completed'))
                if len(dispatch_list) != 0:
                    return HttpHandler.json_response_wrapper(
                        [{'response': {'message': "You can't inactive the selected project, since the project is associated with an active dispatch"
                        , 'status': False}}
                        ], 'Successfull', status.HTTP_200_OK, True
                    )
                else:
                
                    serializer = self.update(request, *args, **kwargs)
                    return HttpHandler.json_response_wrapper(
                        [{'response': {'message': 'Project updated successfully!', 'status': True}}], 'Successfull', status.HTTP_200_OK, True
                    )
            else:
                serializer = self.update(request, *args, **kwargs)
                return HttpHandler.json_response_wrapper(
                    [{'response': {'message': 'Project updated successfully!', 'status': True}}], 'Successfull', status.HTTP_200_OK, True
                )



# from rest_framework.decorators import api_view
# @api_view(['POST'])
# def update(request, *args, **kwargs):

#     data = request.data
#     project = Project.objects.get(id=int(kwargs['pk']))
#     serializer = ProjectSerializer(project, data=data)
#     if serializer.is_valid():
#         serializer.save()
#     else:
#         return HttpHandler.json_response_wrapper(
#                 [{'response': 'Something went wrong'}], 'Failed', 400
#                 )
#     return HttpHandler.json_response_wrapper(
#                 [{'response': serializer.data}], 'Successfull', status.HTTP_200_OK,True
#                 )
