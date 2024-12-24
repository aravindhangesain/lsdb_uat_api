from rest_framework import serializers
from lsdb.models import Unit_pichina
# from lsdb.models import AzureFile
# from lsdb.serializers import AzureFileSerializer
# from lsdb.serializers import ProjectSerializer
# from lsdb.models import Disposition
from lsdb.utils.HasHistory_pichina import unit_history
# from lsdb.utils.NoteUtils import get_note_counts

class UnitList_pichinaSerializer(serializers.HyperlinkedModelSerializer):
    history = serializers.SerializerMethodField()
    model = serializers.ReadOnlyField(source='unit_type.model')
    # unit_images = AzureFileSerializer(AzureFile.objects.all(), many=True, read_only=True)
    location_name = serializers.ReadOnlyField(source='location.name', read_only=True)
    bom = serializers.ReadOnlyField(source='unit_type.bom', read_only=True)
    manufacturer = serializers.ReadOnlyField(source='unit_type.manufacturer.name', read_only=True)
    assigned_test_sequence_name = serializers.SerializerMethodField()
    # notes = serializers.SerializerMethodField()

    # def get_notes(self, obj):
    #     user = self.context.get('request').user
    #     return get_note_counts(user,obj)

    def get_assigned_test_sequence_name(self, obj):
        name = None
        if  obj.procedureresult_pichina_set.count():
            try:
                name = obj.procedureresult_pichina_set.last().test_sequence_definition.name
            except Exception as e:
                name = None
        return name

    def get_history(self, obj):
        return (unit_history(obj))

    class Meta:
        model = Unit_pichina
        fields = [
            'id',
            'url',
            'unit_type',
            'manufacturer',
            # 'fixture_location',
            # 'crate',
            'serial_number',
            'bom',
            'location',
            'location_name',
            'name',
            'model',
            'description',
            # 'notes',
            'history',
            'assigned_test_sequence_name',
            # 'unit_images',
            # 'project_set',
        ]
