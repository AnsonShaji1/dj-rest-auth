from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from .serializers import StackSerializer, StackTypeSerializer
from .models import Stack, StackType
from planner.http import HttpHandler
from rest_framework import status
from rest_framework import generics

from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin

from dispatch.models import Dispatch
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

class StackView(APIView):

    def get(self, request, *args, **kwargs):
        stack = Stack.objects.get(id=int(self.kwargs['pk']))
        serializer = StackSerializer(stack)

        return HttpHandler.json_response_wrapper(
                    [{'response': serializer.data}], 'Successfull', status.HTTP_200_OK,True
                    ) 

    def post(self, request, *args, **kwargs):
        data = request.data        
        serializer = StackSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            return HttpHandler.json_response_wrapper(
                    [{'response': serializer.errors}], 'Failed', 400
                    )

        return HttpHandler.json_response_wrapper(
                    [{'response': serializer.data}], 'Successfull', status.HTTP_200_OK,True
                    )


    def delete(self, request, *args, **kwargs):
        stack = Stack.objects.get(id=int(kwargs['pk']))

        dispatch_list = Dispatch.objects.exclude(
            Q(status__slug='deleted') | Q(status__slug='completed'))
        
        for dispatch in dispatch_list:
            for dis_stack in dispatch.stack.all():
                if (dis_stack.stack.id == stack.id):
                    return HttpHandler.json_response_wrapper(
                        [{'response': {'message': "You can't delete the selected stack, since this stack is associated with an active dispatch"
                        , 'status': False}}], 'Successfull', status.HTTP_200_OK, True
                    )

        stack.status = 'deleted'
        stack.save()

        return HttpHandler.json_response_wrapper(
                    [{'response': {'message': 'Stack deleted sucessfully', 'status': True}}], 'Successfull', status.HTTP_200_OK,True
                    )

    def stack_type(self, request, *args, **kwargs):
        stack_types = StackType.objects.all()
        serializer = StackTypeSerializer(stack_types, many=True)

        return HttpHandler.json_response_wrapper(
                    [{'response': serializer.data}], 'Successfull', status.HTTP_200_OK,True
                    )


class setPagination(PageNumberPagination):
    page_size = 10

class StackList(generics.ListAPIView):
    queryset = Stack.objects.all()
    serializer_class = StackSerializer
    pagination_class = setPagination
    

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset().exclude(status='deleted').order_by('-updated_at')
        queryset = self.paginate_queryset(queryset)
        pageCount = self.paginator.page
        serializer = StackSerializer(queryset, many=True)
        return HttpHandler.json_response_wrapper(
                    [{'num_pages':pageCount.paginator.num_pages,'response': serializer.data}], 'Successfull', status.HTTP_200_OK,True
                    )


class StackUpdate(GenericAPIView, UpdateModelMixin):
    queryset = Stack.objects.all()
    serializer_class = StackSerializer

    # def put(self, request, *args, **kwargs):
    #     serializer = self.update(request, *args, **kwargs)

    #     return HttpHandler.json_response_wrapper(
    #                 [{'response': serializer.data}], 'Successfull', status.HTTP_200_OK,True
    #                 )
    

    def put(self, request, *args, **kwargs):
        data = request.data
        if (data['status']):
            if data['status'] == 'inactive':
                stack_obj = self.get_object()
                dispatch_list = Dispatch.objects.exclude(
                    Q(status__slug='deleted') | Q(status__slug='completed'))
                
                for dispatch in dispatch_list:
                    for dis_stack in dispatch.stack.all():
                        if (dis_stack.stack.id == stack_obj.id):
                            return HttpHandler.json_response_wrapper(
                                [{'response': {'message': "You can't inactivate the selected stack, since this stack is associated with an active dispatch"
                                , 'status': False}}], 'Successfull', status.HTTP_200_OK, True
                            )
                
        serializer = self.update(request, *args, **kwargs)
        return HttpHandler.json_response_wrapper(
            [{'response': {'message': 'Stack updated successfully!', 'status': True}}], 'Successfull', status.HTTP_200_OK,True
        )   



