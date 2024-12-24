from rest_framework import serializers
from lsdb.models import Label
from lsdb.serializers.LabelSerializer import LabelSerializer
from lsdb.models import Note


class EngineeringAgendaSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(Label.objects.all(), many=True, read_only=True)
    username = serializers.ReadOnlyField(source='user.username')
    note_type_name = serializers.ReadOnlyField(source='note_type.name')
    disposition_name = serializers.ReadOnlyField(source='disposition.name')
    disposition_complete = serializers.ReadOnlyField(source='disposition.complete')
    owner_name = serializers.ReadOnlyField(source='owner.username')

    
    class Meta:
        model = Note
        fields = [
            'id',
            'url',
            'user',
            'username',
            'owner',
            'owner_name',
            'datetime',
            'subject',
            'note_type',
            'note_type_name',
            'disposition',
            'disposition_name',
            'disposition_complete',
            'labels'
        ]