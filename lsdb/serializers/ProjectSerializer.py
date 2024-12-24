from rest_framework import serializers

from lsdb.models import Project
from lsdb.models import ExpectedUnitType,LocationLog
from lsdb.serializers.ExpectedUnitTypeSerializer import ExpectedUnitTypeSerializer
from lsdb.utils.HasHistory import measurements_completed, measurements_requested
from lsdb.utils.NoteUtils import get_note_counts

class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    project_manager_name = serializers.ReadOnlyField(source='project_manager.username', read_only=True)
    customer_name = serializers.ReadOnlyField(source='customer.name', read_only=True)
    disposition_name = serializers.ReadOnlyField(source='disposition.name', read_only=True)
    percent_complete = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    note_count = serializers.SerializerMethodField()
    location= serializers.SerializerMethodField()
    # expected_unit_types = ExpectedUnitTypeSerializer(ExpectedUnitType.objects.project_set.all(), read_only=True)
    # expected_unit_types = serializers.SerializerMethodField()
    #
    # def get_expected_unit_types(self, obj):
    #     return ExpectedUnitTypeSerializer(obj.project_set.all(), many=True, context=self.context).data

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
        
    def get_location(self, instance):
        project_id = instance.id
        
        
        latest_location_log = LocationLog.objects.filter(project_id=project_id, is_latest=True).first()
        
        if latest_location_log:
            return latest_location_log.location_id 
        return None 

    class Meta:
        model = Project
        fields = [
            'id',
            'url',
            'number',
            'sfdc_number',
            'project_manager',
            'project_manager_name',
            'customer',
            'customer_name',
            'group',
            'start_date',
            'disposition',
            'disposition_name',
            'proposal_price',
            'percent_complete',
            # 'units',
            'notes',
            'note_count',
            'location',
            'is_pvel',
            # 'expected_unit_types',
        ]
