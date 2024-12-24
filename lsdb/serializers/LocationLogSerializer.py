from rest_framework import serializers
from lsdb.models import LocationLog,Project
from django.db import connection


class LocationLogSerializer(serializers.ModelSerializer):
    unit_id=serializers.ReadOnlyField(source='unit.id')
    location_name=serializers.ReadOnlyField(source='location.name')
    serial_number = serializers.ReadOnlyField(source='unit.serial_number')
    project=serializers.SerializerMethodField()
    project_number=serializers.SerializerMethodField()

    def get_project(self, obj):
        if obj.project is not None:
            return obj.project.id
        else:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT project_id
                    FROM lsdb_project_units
                    WHERE unit_id = %s
                    """,
                    [obj.unit_id]
                )
                result = cursor.fetchone()
            if result:
                return result[0]
            return None
        
    def get_project_number(self, obj):
        project_id=self.get_project(obj)
        project_number=Project.objects.filter(id=project_id).first()
        number=project_number.number
        return number

    
    class Meta:
        model=LocationLog
        fields = [
            'id',
            'project',
            'project_number',
            'location',
            'unit_id',
            'serial_number',
            'datetime',
            'is_latest',
            'asset_id',
            'flag',
            'username',
            'location_name'
        ]

    