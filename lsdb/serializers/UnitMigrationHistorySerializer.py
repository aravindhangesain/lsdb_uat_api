from rest_framework import serializers
from lsdb.models import *

class UnitMigrationHistorySerializer(serializers.ModelSerializer):
    initial_project_number  = serializers.ReadOnlyField(source='initial_project.number')
    initial_workorder_name = serializers.ReadOnlyField(source='initial_workorder.name')
    migrated_project_number  = serializers.ReadOnlyField(source='migrated_project.number')
    migrated_workorder_name = serializers.ReadOnlyField(source='migrated_workorder.name')
    migrated_username  = serializers.ReadOnlyField(source='migrated_by.username')

    class Meta:
        model = UnitMigrationHistory
        fields = [
            'id',
            'initial_serial_number',
            'initial_project_id',
            'initial_project_number',
            'initial_workorder_id',
            'initial_workorder_name',
            'migrated_serial_number',
            'migrated_project_id',
            'migrated_project_number',
            'migrated_workorder_id',
            'migrated_workorder_name',
            'migration_date',
            'migrated_by',
            'migrated_username'
        ]