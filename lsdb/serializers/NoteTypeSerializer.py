from django.contrib.auth.models import User
from rest_framework import serializers

from lsdb.models import NoteType

class NoteTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteType
        fields = [
            'id',
            'url',
            'name',
            'visible_name',
            'description',
            'groups',
        ]
