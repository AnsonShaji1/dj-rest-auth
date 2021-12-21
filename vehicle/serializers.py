from rest_framework import serializers
from .models import Vehicle, VehicleType


class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = '__all__'


class VehicleSerializer(serializers.ModelSerializer):
    vtype = serializers.SerializerMethodField('get_vehicle_type')
    class Meta:
        model = Vehicle
        fields = [
            'id', 'name', 'code', 'vehicle_type', 'vehicle_number',
            'image', 'status', 'user', 'vtype'
        ]

    
    # def create(self, validated_data):
    #     return Project(**validated_data)

    def get_vehicle_type(self, obj):
        try:
            return VehicleTypeSerializer(obj.vehicle_type).data
        except:
            return None


    def validate(self, data):
        return data
    
    # def update(self, instance, validated_data):
    #     return instance


