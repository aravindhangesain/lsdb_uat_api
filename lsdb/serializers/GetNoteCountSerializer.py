from lsdb.models import Project
from rest_framework import serializers

from lsdb.utils.NoteUtils import get_note_counts

class GetNoteCountSerializer(serializers.HyperlinkedModelSerializer):
    notes = serializers.SerializerMethodField()
    note_count = serializers.SerializerMethodField()


    def get_notes(self, obj):
        user = self.context.get('request').user
        return get_note_counts(user,obj)

    def get_note_count(self, obj):
        user = self.context.get('request').user
        notes = get_note_counts(user, obj)
        return len(notes)
    


    class Meta:
        model = Project
        fields = [
            'id',
            'number',
            'notes',
            'note_count'
        ]