from rest_framework import serializers

from lsdb.models import AzureFile
from lsdb.models import Project
from lsdb.models import Crate
from lsdb.models import Note
from lsdb.utils.NoteUtils import get_note_counts

from lsdb.serializers import AzureFileSerializer


class CrateSerializer(serializers.HyperlinkedModelSerializer):
    crate_images = AzureFileSerializer(AzureFile.objects.all(), many=True, read_only=True)
    disposition_name = serializers.ReadOnlyField(source='disposition.name')
    shipped_by_name = serializers.ReadOnlyField(source='shipped_by.name')
    # observations = NoteSerializer(Note.objects.all(), many=True, read_only=True)
    # work_orders = models.ManyToManyField('WorkOrder
    notes = serializers.SerializerMethodField()

    def get_notes(self, obj):
        user = self.context.get('request').user
        return get_note_counts(user,obj)

    class Meta:
        model = Crate
        fields = [
            'id',
            'url',
            'name',
            'disposition_name',
            'disposition',
            'shipped_by_name',
            'shipped_by',
            'shipping_agent',
            'notes',
            'received_date',
            'crate_images',
            'project',
            # 'work_orders',
    ]
