from rest_framework import serializers
from lsdb.models import FinalProcedure

class FinalProcedureSerializer(serializers.ModelSerializer):

    class Meta:
        model=FinalProcedure
        fields=[
            'id',
            'url',
            'selected_procedure',
            'procedure'
        ]