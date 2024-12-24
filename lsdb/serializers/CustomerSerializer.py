from rest_framework import serializers
from lsdb.models import Customer
from lsdb.serializers.NoteSerializer import NoteSerializer


class CustomerSerializer(serializers.HyperlinkedModelSerializer):
    notes = NoteSerializer(many=True, read_only=True)
    project_numbers = serializers.SerializerMethodField()

    def get_project_numbers(self, obj):
        projects = []
        for proj in obj.project_set.all():
            projects.append({"id":proj.id,"number":proj.number})
        return projects

    class Meta:
        model = Customer
        fields = [
            'id',
            'url',
            'name',
            'short_name',
            'project_numbers',
            'notes',
        ]
