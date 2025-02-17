from rest_framework import serializers
from lsdb.models import WorkOrderTemplate


class WorkOrderTemplateSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=WorkOrderTemplate
        fields=[
            'id',
            'url',
            'workorder_name',
            'template_name',
            'description',
            'project',
            'project_number',
            'start_datetime',
            'disposition',
            'unit_disposition',
            'workorder'
            ]