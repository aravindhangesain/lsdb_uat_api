from rest_framework import serializers

from lsdb.models import Customer
from lsdb.models import Project

from lsdb.serializers.ProjectListSerializer import ProjectListSerializer
from lsdb.serializers.NoteSerializer import NoteSerializer

class CustomerDetailSerializer(serializers.HyperlinkedModelSerializer):
    project_set = ProjectListSerializer(many=True, read_only=True)
    notes = NoteSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id',
            'url',
            'name',
            'short_name',
            'notes',
            'project_set',
            'contact_name',
            'contact_email',
            'accounting_email',
            'po_required',
        ]
