from rest_framework import serializers
from lsdb.models import Template
from lsdb.models import FileFormat


class UserProfileTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = [
            'id',
            'url',
            'name',
            'description',
        ]


class TemplateSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    disposition_name = serializers.ReadOnlyField(source='disposition.name')
    group_name = serializers.ReadOnlyField(source='group.name')
    format_name = serializers.ReadOnlyField(source='format.name')

    class Meta:
        model = Template
        fields = [
            'id',
            'url',
            'author',
            'author_name',
            'name',
            'description',
            'disposition',
            'disposition_name',
            'group',
            'group_name',
            'subject_source',
            'body_source',
            'format',
            'format_name',
            # 'byte_code',
        ]
