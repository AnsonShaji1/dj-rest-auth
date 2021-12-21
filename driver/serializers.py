from rest_framework import serializers
from .models import Driver, DriverType


class DriverTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverType
        fields = '__all__'


class DriverSerializer(serializers.ModelSerializer):
    dtype = serializers.SerializerMethodField('get_driver_type')
    format_hour = serializers.SerializerMethodField('get_hour_format')
    class Meta:
        model = Driver
        fields = [
                    'name', 'employee_code', 'driver_type', 'hour', 
                    'image', 'status', 'user', 'dtype', 'id', 'format_hour'
                ]        

    # def create(self, validated_data):
    #     return Project(**validated_data)

    def get_driver_type(self, obj):
        try:
            return DriverTypeSerializer(obj.driver_type).data
        except:
            return None
    
    def get_hour_format(self, data):
        if len(str(data.hour.hour)) > 1:
            hour = str(data.hour.hour)
        else:
            hour = '0' + str(data.hour.hour)
        if len(str(data.hour.minute)) > 1:
            minute = str(data.hour.minute)
        else:
            minute = '0' + str(data.hour.minute)
        
        return hour + ':' + minute

    def validate(self, data):
        return data
    
    # def update(self, instance, validated_data):
    #     return instance

