from rest_framework import serializers

from lsdb.models import *

class UserAssignmentForProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserAssignmentForProcedure
        fields=[
                'id',
                'user_id',
                'procedure_result_id',
                'assigned_on',
                'assigned_by',
                'due_date'
            ]
        read_only_fields = ('assigned_by',)
    
    