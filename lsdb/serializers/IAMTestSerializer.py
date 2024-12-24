from rest_framework import serializers
from django.db import connection
from lsdb.models import Unit

class IAMTestSerializer(serializers.ModelSerializer):
    projects = serializers.SerializerMethodField()
    workorders = serializers.SerializerMethodField()
    module_properties = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = [
            'id',
            'serial_number',
            'projects',
            'workorders',
            'module_properties'
        ]

    def get_projects(self, obj):
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT p.id, p.number, p.customer_id, c.name
                FROM lsdb_project_units pu
                JOIN lsdb_project p ON pu.project_id = p.id
                JOIN lsdb_customer c ON p.customer_id = c.id
                WHERE pu.unit_id = %s
            ''', [obj.id])
            projects = cursor.fetchall()

            return [
                {
                    'project_number': project[1],
                    'customer_name': project[3]
                } for project in projects
            ] if projects else []

    def get_workorders(self, obj):
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT wo.id, wo.name,wo.start_datetime
                FROM lsdb_workorder_units wu
                JOIN lsdb_workorder wo ON wu.workorder_id = wo.id
                WHERE wu.unit_id = %s
            ''', [obj.id])
            workorders = cursor.fetchall()

            return [
                {
                    'BOM': workorder[1],
                    'NTP':workorder[2]
                } for workorder in workorders
            ] if workorders else []

    def get_module_properties(self, obj):
        with connection.cursor() as cursor:
            # Fetch the unittype_id from the unit table
            cursor.execute('''
                SELECT unit_type_id
                FROM lsdb_unit
                WHERE id = %s
            ''', [obj.id])
            unittype_id = cursor.fetchone()
        
            if not unittype_id:
                return []

            unittype_id = unittype_id[0]
        
            # Fetch the module_property_id from the unittype table
            cursor.execute('''
                SELECT module_property_id
                FROM lsdb_unittype
                WHERE id = %s
            ''', [unittype_id])
            module_property_id = cursor.fetchone()
        
            if not module_property_id:
                return []

            module_property_id = module_property_id[0]
        
            # Fetch data from the module_property table using the module_property_id
            cursor.execute('''
                SELECT mp.number_of_cells, mp.module_width,mp.module_height,mp.isc,mp.alpha_isc,
                    mt.name as module_technology_name
                FROM lsdb_moduleproperty mp
                JOIN lsdb_moduletechnology mt ON mp.module_technology_id = mt.id
                WHERE mp.id = %s
            ''', [module_property_id])
            module_properties = cursor.fetchall()
        
            return [
                {
                    'Number_of_Cells': property[0],
                    'Cell_Width': property[1],
                    'Cell_Height':property[2],
                    'Isc':property[3],
                    'Alpha_Isc':property[4],
                    'Cell_Type': property[5]
                } for property in module_properties
            ] if module_properties else []