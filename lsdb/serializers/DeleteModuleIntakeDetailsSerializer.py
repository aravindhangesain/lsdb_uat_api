from rest_framework import serializers
from lsdb.models import ModuleIntakeDetails

class DeleteModuleIntakeDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ModuleIntakeDetails
        fields = [
            'id',
            'url'      
        ]







