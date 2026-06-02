from rest_framework import serializers
from accesscontrol.models import ERPPermission, ERPRolePermission


class ERPPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ERPPermission
        fields = '__all__'


class ERPRolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ERPRolePermission
        fields = '__all__'


