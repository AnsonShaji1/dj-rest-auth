from rest_framework import serializers
from .models import Project
from dispatch.models import Dispatch


class ProjectSerializer(serializers.ModelSerializer):
    travel_time_format = serializers.SerializerMethodField('get_travel_time_format')
    remaining_sqm_time = serializers.SerializerMethodField('get_remaining_sqm_time')
    class Meta:
        model = Project
        fields = [
            'name', 'code', 'travel_time', 'total_order', 'contact_name',
            'contact_mob', 'address_line_1', 'address_line_2', 'status',
            'user', 'travel_time_format', 'id', 'remaining_sqm_time'
        ]

    # def create(self, validated_data):
    #     return Project(**validated_data)

    def validate(self, data):
        return data
    
    def get_travel_time_format(self, data):
        if len(str(data.travel_time.hour)) > 1:
            hour = str(data.travel_time.hour)
        else:
            hour = '0' + str(data.travel_time.hour)

        if len(str(data.travel_time.minute)) > 1:
            minute = str(data.travel_time.minute)
        else:
            minute = '0' + str(data.travel_time.minute)
        
        return hour + ':' + minute

    def get_remaining_sqm_time(self, data):
        try:
            dispatch_list = Dispatch.objects.filter(project__id=data.id).exclude(status__slug='deleted')
            sqm_value = 0
            for i in dispatch_list:
                for j in i.stack.all():
                    sqm_value = sqm_value + j.payload
            remaining_sqm = data.total_order - sqm_value
            return remaining_sqm
        except:
            return 0

                    
    # def update(self, instance, validated_data):
    #     return instance
