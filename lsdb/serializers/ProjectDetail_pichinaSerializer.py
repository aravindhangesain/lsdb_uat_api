from rest_framework import serializers
from django.db.models import Max

from lsdb.models import Unit_pichina, Workorder_pichina
from lsdb.models import Project_pichina
from lsdb.serializers.UnitList_pichinaSerializer import UnitList_pichinaSerializer
from lsdb.serializers.WorkorderList_pichinaSerializer import WorkorderList_pichinaSerializer


class ProjectDetail_pichinaSerializer(serializers.HyperlinkedModelSerializer):
    # attachments = AzureFileSerializer(AzureFile.objects.all(), many=True, read_only=True)
    project_manager_name = serializers.ReadOnlyField(source='project_manager.username', read_only=True)
    customer_name = serializers.ReadOnlyField(source='customer.name', read_only=True)
    disposition_name = serializers.ReadOnlyField(source='disposition.name', read_only=True)
    workorder_set = serializers.SerializerMethodField()
    # expectedunittype_set = ExpectedUnitTypeSerializer(many=True, read_only=True)
    # actions = ActionResultSerializer(many=True, read_only=True)
    units = serializers.SerializerMethodField()
    # notes = serializers.SerializerMethodField()
    # crates = serializers.SerializerMethodField()
    # location=serializers.SerializerMethodField()
    # last_action_datetime = serializers.SerializerMethodField()
    # note_count = serializers.SerializerMethodField()
    # sri_notes = NoteSerializer(many=True, read_only=True)
    # expected_unit_types = ExpectedUnitTypeSerializer(ExpectedUnitType.objects.project_set.all(), read_only=True)
    # expected_unit_types = serializers.SerializerMethodField()
    #
    # def get_expected_unit_types(self, obj):
    #     return ExpectedUnitTypeSerializer(obj.project_set.all(), many=True, context=self.context).data

    # def get_notes(self, obj):
    #     user = self.context.get('request').user
    #     return get_note_counts(user, obj)

    # def get_last_action_datetime(self, obj):
    #     # need highest date of completed procedure result
    #     date_time = MeasurementResult_pichina.objects.filter(step_result__procedure_result__unit__project=obj).aggregate(
    #         Max('date_time'))
    #     if date_time:
    #         return date_time["date_time__max"]
    #     else:
    #         return None
        
    def get_workorder_set(self, obj):
        workorders = Workorder_pichina.objects.filter(project_id=obj.id)
        return WorkorderList_pichinaSerializer(workorders, many=True, context=self.context).data
    
    def get_units(self, obj):
        unit_ids = obj.get_units(unit_type=None) 
        units = Unit_pichina.objects.filter(id__in=unit_ids)
        return UnitList_pichinaSerializer(units, many=True, context=self.context).data
    

    # def get_note_count(self, obj):
    #     user = self.context.get('request').user
    #     notes = get_note_counts(user, obj)
    #     return len(notes)

    # def get_crates(self, obj):
    #     crates = Crate.objects.filter(project=obj).distinct()
    #     return CrateSerializer(crates, many=True, context=self.context).data
    
    # def get_location(self, instance):
    #     project_id = instance.id
    #     latest_location_log = LocationLog.objects.filter(project_id=project_id, is_latest=True).first()
    #     if latest_location_log:
    #         return latest_location_log.location_id 
    #     return None 

    class Meta:
        model = Project_pichina
        fields = [
            'id',
            'url',
            'number',
            'sfdc_number',
            'project_manager',
            'project_manager_name',
            'customer',
            'customer_name',
            'workorder_set',
            # 'group',
            'start_date',
            'disposition',
            'disposition_name',
            # 'expectedunittype_set',
            # 'actions',
            'units',
            # 'notes',
            # 'note_count',
            # 'attachments',
            # 'last_action_datetime',
            # 'crates',
            'proposal_price',
            # 'location',
            # 'sri_notes',
            # 'expected_unit_types',
        ]
