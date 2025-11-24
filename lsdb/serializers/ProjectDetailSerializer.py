from rest_framework import serializers
from django.db.models import Max

from lsdb.models import AzureFile
from lsdb.models import Project
from lsdb.models import *
from lsdb.models import WorkOrder
from lsdb.models import ExpectedUnitType,LocationLog
from lsdb.models import Note
from lsdb.models import MeasurementResult
from lsdb.models import Crate
from lsdb.serializers import AzureFileSerializer, ActionResultSerializer
from lsdb.serializers import CrateSerializer
from lsdb.serializers import UnitListSerializer
from lsdb.serializers import NoteSerializer
from lsdb.serializers import ExpectedUnitTypeSerializer
from lsdb.serializers import WorkOrderListSerializer
from lsdb.serializers import ExpectedUnitTypeSerializer
from lsdb.utils.NoteUtils import get_note_counts


class ProjectDetailSerializer(serializers.HyperlinkedModelSerializer):
    attachments = AzureFileSerializer(AzureFile.objects.all(), many=True, read_only=True)
    project_manager_name = serializers.ReadOnlyField(source='project_manager.username', read_only=True)
    customer_name = serializers.ReadOnlyField(source='customer.name', read_only=True)
    disposition_name = serializers.ReadOnlyField(source='disposition.name', read_only=True)
    workorder_set = WorkOrderListSerializer(many=True, read_only=True)
    # expectedunittype_set = ExpectedUnitTypeSerializer(many=True, read_only=True)
    actions = ActionResultSerializer(many=True, read_only=True)
    units = UnitListSerializer(many=True, read_only=True)
    notes = serializers.SerializerMethodField()
    # crates = serializers.SerializerMethodField()
    location=serializers.SerializerMethodField()

    last_action_datetime = serializers.SerializerMethodField()

    note_count = serializers.SerializerMethodField()

    factory_witness = serializers.SerializerMethodField()

    # sri_notes = NoteSerializer(many=True, read_only=True)

    # expected_unit_types = ExpectedUnitTypeSerializer(ExpectedUnitType.objects.project_set.all(), read_only=True)
    # expected_unit_types = serializers.SerializerMethodField()
    #
    # def get_expected_unit_types(self, obj):
    #     return ExpectedUnitTypeSerializer(obj.project_set.all(), many=True, context=self.context).data

    def get_notes(self, obj):
        user = self.context.get('request').user
        return get_note_counts(user, obj)

    def get_last_action_datetime(self, obj):
        # need highest date of completed procedure result
        date_time = MeasurementResult.objects.filter(step_result__procedure_result__unit__project=obj).aggregate(
            Max('date_time'))
        if date_time:
            return date_time["date_time__max"]
        else:
            return None

    def get_note_count(self, obj):
        user = self.context.get('request').user
        notes = get_note_counts(user, obj)
        return len(notes)

    def get_crates(self, obj):
        crates = Crate.objects.filter(project=obj).distinct()
        return CrateSerializer(crates, many=True, context=self.context).data
    
    def get_location(self, instance):
        project_id = instance.id
        
        
        latest_location_log = LocationLog.objects.filter(project_id=project_id, is_latest=True).first()
        
        if latest_location_log:
            location= latest_location_log.location_id
            return ("https://lsdbhaveblueuat.azurewebsites.net/api/1.0/locations/"+str(location)+"/")
        return None
    
    def get_factory_witness(self, obj):
        if ProjectFactoryWitness.objects.filter(project=obj).exists():
            return True
        return False


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
            'workorder_set',
            # 'expectedunittype_set',
            'actions',
            'units',
            'notes',
            'note_count',
            'attachments',
            'last_action_datetime',
            # 'crates',
            'proposal_price',
            'location',
            'factory_witness'
            # 'sri_notes',
            # 'expected_unit_types',
        ]
