from rest_framework import serializers
from lsdb.models import ActionDefinition

# ProcedureDefinitionSerializer...
class ActionDefinitionSerializer(serializers.HyperlinkedModelSerializer):
    disposition_name = serializers.SerializerMethodField()

    def get_disposition_name(self, obj):
        if obj.disposition:
            return obj.disposition.name
        else:
            return None

    class Meta:
        model = ActionDefinition
        fields = [
            'id',
            'url',
            'name',
            'description',
            'disposition',
            'disposition_name',
            'completion_criteria',
            'groups',
        ]
