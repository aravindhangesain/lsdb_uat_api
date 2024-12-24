from rest_framework import serializers
from lsdb.models import AuthUser_pichina

class AuthUser_pichinaSerializer(serializers.SerializerMethodField):
    class Meta:
        model = AuthUser_pichina
        fields = [
            'id',
            'password',
            'last_login',
            'is_superuser',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_active',
            'date_joined'
        ]