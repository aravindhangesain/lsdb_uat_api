from django.contrib.auth.models import User
from rest_framework import serializers

from lsdb.models import Notetype_pichina

class Notetype_pichinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notetype_pichina
        fields = [
            'id',
            'url',
            'name',
            'visible_name',
            'description',
            'groups',
        ]
