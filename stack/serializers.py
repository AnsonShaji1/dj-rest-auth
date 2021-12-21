from rest_framework import serializers
from .models import Stack, StackType


class StackTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StackType
        fields = '__all__'


class StackSerializer(serializers.ModelSerializer):
    stype = serializers.SerializerMethodField('get_stack_type')
    class Meta:
        model = Stack
        fields = [
            'id', 'code', 'stack_type', 'stack_number',
            'quantity', 'image', 'status', 'user', 'stype'
        ]

    def validate(self, data):
        return data

    def get_stack_type(self, obj):
        try:
            return StackTypeSerializer(obj.stack_type).data
        except:
            return None


