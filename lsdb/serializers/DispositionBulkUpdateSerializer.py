from rest_framework import serializers
from lsdb.models import Project


class DispositionBulkUpdateSerializer(serializers.HyperlinkedModelSerializer):
    disposition_name = serializers.ReadOnlyField(source='disposition.name', read_only=True)


    class Meta:
        model = Project
        fields = [
            'disposition',
            'disposition_name',           
        ]
