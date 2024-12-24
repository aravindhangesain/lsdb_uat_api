from rest_framework import serializers
from lsdb.models import Project
from lsdb.utils.NoteUtils import get_note_counts
from lsdb.utils.HasHistory import measurements_completed, measurements_requested


class ProposalPriceField(serializers.FloatField):
    def to_internal_value(self, data):

        # Allow empty strings to be converted to None
        if data in ('', 'null'):
            return None
        
        return super().to_internal_value(data)


class StartdateField(serializers.DateField):
    def to_internal_value(self, data):
        # Allow empty strings to be converted to None
        if data in ('', 'null'):
            return None
        return super().to_internal_value(data)


class UpdateProjectDetailsSerializer(serializers.HyperlinkedModelSerializer):
    project_manager_name = serializers.ReadOnlyField(source='project_manager.username', read_only=True)
    disposition_name = serializers.ReadOnlyField(source='disposition.name', read_only=True)
    percent_complete = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    note_count = serializers.SerializerMethodField()
    proposal_price= ProposalPriceField(allow_null=True, required=False)
    comments = serializers.CharField(write_only=True)
    start_date = StartdateField(required=False, allow_null=True)
    
    def get_notes(self, obj):
        user = self.context.get('request').user
        return get_note_counts(user,obj)
    def get_note_count(self, obj):
        user = self.context.get('request').user
        notes = get_note_counts(user, obj)
        return len(notes)
    def get_percent_complete(self, obj):
        measurements = measurements_requested(obj)
        if measurements == 0:
            return 0
        else:
            return int(100 * (measurements_completed(obj) / measurements))
    class Meta:
        model = Project
        fields = [
            'id',
            'url',
            'sfdc_number',
            'project_manager',
            'project_manager_name',
            'group',
            'start_date',
            'disposition',
            'disposition_name',
            'proposal_price',
            'percent_complete',
            'notes',
            'note_count',
            'comments',
        ]
