from rest_framework import serializers
from lsdb.models import WorkOrderTemplate


class WorkOrderTemplateSerializer(serializers.HyperlinkedModelSerializer):

    workorder_id=serializers.ReadOnlyField(source='workorder.id')

    class Meta:
        model=WorkOrderTemplate
        fields=[
            'id',
            'url',
            'workorder_id',
            'workorder',
            'template_name'
            ]