from rest_framework import serializers
from .models import Dispatch, DispatchStack, StackStatus, DispatchStatus, DelayReason
from project.models import Project
from vehicle.models import Vehicle
from stack.models import Stack
from driver.models import Driver


class DispatchStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DispatchStatus
        fields = '__all__'

class StackStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = StackStatus
        fields = '__all__'


class DelayReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = DelayReason
        fields = '__all__'


class DispatchProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'code', 'travel_time']


class DispatchVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'name', 'vehicle_number']


class DispatchDriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['id', 'name', 'hour']


class DispatchStackSerializer(serializers.ModelSerializer):
    stype = serializers.SerializerMethodField('get_stack_type')

    class Meta:
        model = Stack
        fields = ['id', 'stype', 'code', 'stack_number']

    def get_stack_type(self, obj):
        return obj.stack_type.name


class NestedStackSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    stack_detail = serializers.SerializerMethodField('get_stack_instance')
    status_detail = serializers.SerializerMethodField('get_status_detail')
    dispatch_detail = serializers.SerializerMethodField('get_dispatch_detail')

    class Meta:
        model = DispatchStack
        fields = [
            'id', 'stack', 'payload', 'weight', 'panel_number',
            'status', 'stack_detail', 'status_detail', 'dispatch_detail'
        ]

    def get_dispatch_detail(self, obj):
        try:
            dispatch = obj.dispatch_set.all()[0]
            data = {
                'project_name': dispatch.project.name,
                'despatch_ref': dispatch.reference,
                'dispatch_date': dispatch.date.date().strftime('%Y-%m-%d'),
                'code': dispatch.code,
                'color': dispatch.status.color
            }
            return data

        except:
            return None

    def get_stack_instance(self, obj):
        try:
            return DispatchStackSerializer(obj.stack).data
        except:
            return None

    def get_status_detail(self, obj):
        try:
            return StackStatusSerializer(obj.status).data
        except:
            return None


class DispatchSerializer(serializers.ModelSerializer):
    stack = NestedStackSerializer(many=True)
    pro_obj = serializers.SerializerMethodField('get_project_instance')
    dri_obj = serializers.SerializerMethodField('get_driver_instance')
    vehi_obj = serializers.SerializerMethodField('get_vehicle_instance')
    formatted_date = serializers.SerializerMethodField('get_formatted_date')
    formatted_start_time = serializers.SerializerMethodField(
        'get_formatted_start_time')
    formatted_approx_time = serializers.SerializerMethodField(
        'get_formatted_approx_time')
    formatted_return_time = serializers.SerializerMethodField(
        'get_formatted_return_time')
    approx_time_bk = serializers.SerializerMethodField('get_approx_time_bk')
    start_time_bk = serializers.SerializerMethodField('get_start_time_bk')
    status_name = serializers.SerializerMethodField('get_status_name')
    delay_reason_name = serializers.SerializerMethodField('get_delay_reason_name')

    class Meta:
        model = Dispatch
        fields = [
            'id', 'project', 'vehicle', 'driver', 'date',
            'start_time', 'approx_time', 'reference',
            'stack', 'status', 'pro_obj', 'dri_obj', 'vehi_obj',
            'formatted_date', 'formatted_approx_time', 'formatted_start_time',
            'start_time_bk', 'approx_time_bk', 'status_name', 'code',
            'return_time', 'delay_reason', 'optional_reason', 'remarks',
            'note', 'delay_reason_name', 'formatted_return_time'
        ]

    def get_formatted_return_time(self, obj):
        try:
            return obj.return_time.strftime('%I:%M %p')
        except:
            return None


    def get_delay_reason_name(self, obj):
        try:
            return obj.delay_reason.name
        except:
            return None

    def get_status_name(self, obj):
        try:
            return obj.status.name
        except:
            return None

    def get_approx_time_bk(self, obj):
        try:
            return obj.approx_time
        except:
            return None

    def get_start_time_bk(self, obj):
        try:
            return obj.start_time
        except:
            return None

    def get_project_instance(self, obj):
        try:
            return DispatchProjectSerializer(obj.project).data
        except:
            return None

    def get_driver_instance(self, obj):
        try:
            return DispatchDriverSerializer(obj.driver).data
        except:
            return None

    def get_vehicle_instance(self, obj):
        try:
            return DispatchVehicleSerializer(obj.vehicle).data
        except:
            return None

    def get_formatted_date(self, obj):
        try:
            return obj.date.date().strftime('%Y-%m-%d')
        except:
            return None

    def get_formatted_start_time(self, obj):
        try:
            return obj.start_time.strftime('%I:%M %p')
        except:
            return None

    def get_formatted_approx_time(self, obj):
        try:
            return obj.approx_time.strftime('%I:%M %p')
        except:
            return None

    def create(self, validated_data):
        stacks_data = validated_data.pop('stack')
        dispatch_obj = Dispatch.objects.create(**validated_data)
        stack_list = []  # it will contains list of Building model instance
        for stack_item in stacks_data:
            dis_stack_id = stack_item.pop('id', None)
            stack_obj, _ = DispatchStack.objects.get_or_create(id=dis_stack_id,
                                                               defaults=stack_item)
            stack_list.append(stack_obj)
        # add all passed instances of Building model to BuildingGroup instance
        dispatch_obj.stack.add(*stack_list)
        return dispatch_obj

    def update(self, instance, validated_data):
        stacks_data = validated_data.pop('stack')
        instance.reference = validated_data.get(
            'reference', instance.reference)
        instance.project = validated_data.get('project', instance.project)
        instance.vehicle = validated_data.get('vehicle', instance.vehicle)
        instance.driver = validated_data.get('driver', instance.driver)
        instance.date = validated_data.get('date', instance.date)
        instance.note = validated_data.get('note', instance.note)
        instance.start_time = validated_data.get(
            'start_time', instance.start_time)
        instance.approx_time = validated_data.get(
            'approx_time', instance.approx_time)
        instance.status = validated_data.get('status', instance.status)

        instance.stack.all().delete()
        stack_list = []
        for stack_item in stacks_data:
            dis_stack_id = stack_item.pop('id', None)
            stack_obj, _ = DispatchStack.objects.get_or_create(id=dis_stack_id,
                                                               defaults=stack_item)
            if dis_stack_id:
                stack_obj.stack = stack_item.get('stack', stack_obj.stack)
                stack_obj.payload = stack_item.get(
                    'payload', stack_obj.payload)
                stack_obj.weight = stack_item.get('weight', stack_obj.weight)
                stack_obj.panel_number = stack_item.get(
                    'panel_number', stack_obj.panel_number)
                stack_obj.status = stack_item.get('status', stack_obj.status)
                stack_obj.save()
            stack_list.append(stack_obj)
        instance.stack.add(*stack_list)

        # if 'id' in stack_item:
        #     dispatch_stack = DispatchStack.objects.get(id=stack_item.get('id'))
        #     dispatch_stack.payload = stack_item.get('payload', dispatch_stack.payload)
        #     dispatch_stack.weight = stack_item.get('weight', dispatch_stack.weight)
        #     dispatch_stack.panel_number = stack_item.get('panel_number', dispatch_stack.panel_number)
        #     dispatch_stack.stack = stack_item.get('stack', dispatch_stack.stack)
        #     dispatch_stack.status = stack_item.get('status', dispatch_stack.status)
        #     dispatch_stack.save()
        # else:
        #     dis_stack_id = stack_item.pop('id', None)
        #     stack_obj, _ = DispatchStack.objects.get_or_create(id=dis_stack_id,
        #     defaults=stack_item)
        #     instance.stack.add(stack_obj)
        instance.save()

        return instance

    def validate(self, data):
        return data

    # def update(self, instance, validated_data):
    #     return instance


class DispatchTimePlotSerializer(serializers.ModelSerializer):
    start = serializers.SerializerMethodField('get_start_time')
    end = serializers.SerializerMethodField('get_end_time')
    title = serializers.SerializerMethodField('get_title')
    color = serializers.SerializerMethodField('set_color')
    driver_name = serializers.SerializerMethodField('get_driver_name')
    vehicle_name = serializers.SerializerMethodField('get_vehicle_name')

    class Meta:
        model = Dispatch
        fields = [
            'start', 'end', 'title', 'color', 'id', 'reference',
            'driver_name', 'vehicle_name', 'return_time'
        ]

    def get_title(self, obj):
        try:
            return obj.project.name
        except:
            return None

    def get_driver_name(self, obj):
        try:
            return obj.driver.name
        except:
            return None

    def get_vehicle_name(self, obj):
        try:
            return obj.vehicle.name
        except:
            return None

    def set_color(self, obj):
        return {'primary': "#e3bc08", 'secondary': "#FDF1BA"}

    def get_start_time(self, obj):
        try:
            return obj.start_time
        except:
            return None

    def get_end_time(self, obj):
        try:
            return obj.approx_time
        except:
            return None