from rest_framework import serializers
from lsdb.models import ProjectTemplate


class ProjectTemplateSerializer(serializers.HyperlinkedModelSerializer):

    project_id=serializers.ReadOnlyField(source='project.id')

    class Meta:
        model=ProjectTemplate
        fields=[
            'id',
            'url',
            'project_id',
            'project',
            'template_name'
            ]