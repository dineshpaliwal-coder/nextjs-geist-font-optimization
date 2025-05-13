from rest_framework import serializers
from .models import User, Role

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'job_title',
                 'department', 'is_active', 'is_tenant_admin', 'language',
                 'timezone', 'date_format', 'time_format', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name', 'description', 'can_manage_users', 'can_manage_roles',
                 'can_manage_clients', 'can_manage_projects', 'can_manage_invoices',
                 'can_manage_expenses', 'can_manage_settings', 'custom_permissions',
                 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
