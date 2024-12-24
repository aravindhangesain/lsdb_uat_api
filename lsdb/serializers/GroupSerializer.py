from rest_framework import serializers
from lsdb.models import Group

from lsdb.serializers.UserListSerializer import UserListSerializer
from lsdb.serializers.TestSequenceDefinitionSerializer import TestSequenceDefinitionSerializer
from lsdb.serializers.NoteTypeSerializer import NoteTypeSerializer

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    users = UserListSerializer(many=True, read_only=True)
    test_sequence_definitions = TestSequenceDefinitionSerializer(source='testsequencedefinition_set', many=True, read_only=True)
    note_types = NoteTypeSerializer(source='notetypes_set', many=True, read_only=True)

    class Meta:
        model = Group
        fields = [
            'id',
            'url',
            'name',
            'notes',
            'organization',
            'group_type',
            'users',
            'test_sequence_definitions',
            'note_types',
        ]
