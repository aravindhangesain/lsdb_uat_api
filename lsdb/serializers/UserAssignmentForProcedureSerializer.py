from rest_framework import serializers

from lsdb.models import *

class UserAssignmentForProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserAssignmentForProcedure
        fields='__all__'
        read_only_fields = ('assigned_by',)
    
    