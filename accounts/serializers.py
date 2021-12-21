from rest_framework import serializers

from .models import User, UserRole

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['id', 'name', 'slug']

class UserSerializer(serializers.ModelSerializer):
    user_role = serializers.SerializerMethodField('get_user_role')
    user_role_slug = serializers.SerializerMethodField('get_user_role_slug')
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 
            'last_name', 'employee_code', 'employee_role',
            'status', 'user_role', 'user_role_slug'
            ]
    def get_user_role(self, obj):
        try:
            return obj.employee_role.name
        except:
            return None

    def get_user_role_slug(self, obj):
        try:
            return obj.employee_role.slug
        except:
            return None
