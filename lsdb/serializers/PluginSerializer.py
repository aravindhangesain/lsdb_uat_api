from rest_framework import serializers
from lsdb.models import Plugin


class PluginSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    disposition_name = serializers.ReadOnlyField(source='disposition.name')
    reviewer_name = serializers.ReadOnlyField(source='reviewed_by_user.username')
    group_name = serializers.ReadOnlyField(source='group.name')

    class Meta:
        model = Plugin
        fields = [
            'id',
            'url',
            'author',
            'author_name',
            'name',
            'description',
            'disposition',
            'disposition_name',
            'reviewed_by_user',
            'reviewer_name',
            'review_datetime',
            'revision',
            'group',
            'group_name',
            'source_code',
            # 'byte_code',
            'restricted',
        ]
