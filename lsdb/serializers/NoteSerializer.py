from django.contrib.auth.models import User
from django.db.models import Max

from rest_framework import serializers

from lsdb.models import Label
from lsdb.serializers.LabelSerializer import LabelSerializer
from lsdb.models import AzureFile
from lsdb.serializers import AzureFileSerializer
from lsdb.models import Note
from django.db import connection


class ObjectSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'model_name': instance._meta.model_name,
            'id':instance.id,
            'str':str(instance.__str__())
        }

class NoteSerializer(serializers.ModelSerializer):
    attachments = AzureFileSerializer(AzureFile.objects.all(), many=True, read_only=True)
    labels = LabelSerializer(Label.objects.all(), many=True, read_only=True)
    tagged_users = serializers.SerializerMethodField()
    owner_name = serializers.ReadOnlyField(source='owner.username')
    username = serializers.ReadOnlyField(source='user.username')
    note_type_name = serializers.ReadOnlyField(source='note_type.name')
    disposition_name = serializers.ReadOnlyField(source='disposition.name')
    disposition_complete = serializers.ReadOnlyField(source='disposition.complete')
    read = serializers.SerializerMethodField()
    last_update_datetime = serializers.SerializerMethodField()
    parent_objects = serializers.SerializerMethodField()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        obj = Note.objects.create(**validated_data)
        obj.save()
        return obj

    def get_last_update_datetime(self, obj):
        # need highest date of all chlid notes:
        date_time = Note.objects.filter(parent_note=obj).aggregate(Max('datetime')).get('datetime__max')
        if date_time:
            return date_time
        else:
            return obj.datetime

    def get_read(self, obj):
        user = self.context.get('request').user
        return bool(obj.notereadstatus_set.filter(user=user).count())

    def get_parent_objects(self, obj):
        # because we don't always know what models have a realtion to
        # us, we need to interrogate the _meta
        parent_objects = []
        related_objects = obj._meta.related_objects
        for object in related_objects:
            if object.remote_field.name == 'notes':
                # we know we're looking at a reverse accessor to notes:
                parents = object.remote_field.model.objects.filter(notes__in=[obj.id])
                for parent in parents:
                    serializer = ObjectSerializer(parent)
                    parent_objects.append(serializer.data)
        return parent_objects

    def get_tagged_users(self, obj):
        queryset = obj.tagged_users.all()
        userStruct = []
        for user in queryset:
            temp = {
                "id": user.id,
                "username": user.username,
            }
            userStruct.append(temp)
        return userStruct

    class Meta:
        model = Note
        fields = [
            'id',
            'url',
            'user',
            'username',
            'owner',
            'owner_name',
            'parent_note',
            'datetime',
            'last_update_datetime',
            'subject',
            'text',
            'note_type',
            'note_type_name',
            'disposition',
            'disposition_name',
            'disposition_complete',
            'read',
            # 'organization',
            'attachments',
            'labels',
            'groups',
            'tagged_users',
            'parent_objects',
        ]
        
class ReportBuildSerializer(serializers.HyperlinkedModelSerializer):
    serial_number = serializers.SerializerMethodField()
    project_number = serializers.SerializerMethodField()
    test_sequence_name = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    note_attachment_id = serializers.SerializerMethodField()
    tagged_users = serializers.SerializerMethodField()
    manufacturer = serializers.SerializerMethodField()
    bom = serializers.SerializerMethodField()
    module_model = serializers.SerializerMethodField()
    pmax = serializers.SerializerMethodField()
    note_type_name = serializers.ReadOnlyField(source='note_type.name')
    author_name = serializers.ReadOnlyField(source='user.username')
    owner_name = serializers.ReadOnlyField(source='owner.username')
    
    def get_serial_number(self, obj):
        note_id = obj.id
        if not note_id:
            return None
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.serial_number FROM lsdb_unit_notes un 
                JOIN lsdb_unit u ON un.unit_id = u.id
                WHERE un.note_id = %s
            """, [note_id])
            result = cursor.fetchone()
            return result[0] if result else None
        
    def get_bom(self, obj):
        note_id = obj.id
        if not note_id:
            return None
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT wo.name FROM lsdb_project_notes pn 
                JOIN lsdb_project p ON pn.project_id = p.id
                JOIN lsdb_workorder wo ON p.id = wo.project_id
                WHERE pn.note_id = %s
            """, [note_id])
            result = cursor.fetchone()
            return result[0] if result else None
        
    def get_project_number(self, obj):
        note_id = obj.id
        if not note_id:
            return None
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.number FROM lsdb_project_notes pn 
                JOIN lsdb_project p ON pn.project_id = p.id
                WHERE pn.note_id = %s
            """, [note_id])
            result = cursor.fetchone()
            return result[0] if result else None
        
    def get_test_sequence_name(self, obj):
        note_id = obj.id
        if not note_id:
            return None
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tsd.name FROM lsdb_unit_notes un 
                JOIN lsdb_unit u ON un.unit_id = u.id
                Join lsdb_procedureresult pr ON u.id = pr.unit_id
                Join lsdb_testsequencedefinition tsd ON pr.test_sequence_definition_id = tsd.id
                WHERE un.note_id = %s
            """, [note_id])
            result = cursor.fetchone()
            return result[0] if result else None
        
    def get_customer_name(self, obj):
        note_id = obj.id
        if not note_id:
            return None
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT c.name FROM lsdb_project_notes pn 
                JOIN lsdb_project p ON pn.project_id = p.id
                Join lsdb_customer c ON p.customer_id = c.id
                WHERE pn.note_id = %s
            """, [note_id])
            result = cursor.fetchone()
            return result[0] if result else None
        
    def get_manufacturer(self, obj):
        note_id = obj.id
        if not note_id:
            return None
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT c.name FROM lsdb_project_notes pn 
                JOIN lsdb_project p ON pn.project_id = p.id
                Join lsdb_customer c ON p.customer_id = c.id
                WHERE pn.note_id = %s
            """, [note_id])
            result = cursor.fetchone()
            return result[0] if result else None
        
    def get_module_model(self, obj):
        note_id = obj.id
        if not note_id:
            return None
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ut.model FROM lsdb_unit_notes un 
                JOIN lsdb_unit u ON un.unit_id = u.id
                Join lsdb_unittype ut ON u.unit_type_id = ut.id
                WHERE un.note_id = %s
            """, [note_id])
            result = cursor.fetchone()
            return result[0] if result else None
        
    def get_pmax(self, obj):
        note_id = obj.id
        if not note_id:
            return None
        with connection.cursor() as cursor:
            cursor.execute("""
               SELECT mp.nameplate_pmax FROM lsdb_unit_notes un 
                JOIN lsdb_unit u ON un.unit_id = u.id
                Join lsdb_unittype ut ON u.unit_type_id = ut.id
                Join lsdb_moduleproperty mp ON mp.id = ut.module_property_id
                WHERE un.note_id = %s
            """, [note_id])
            result = cursor.fetchone()
            return result[0] if result else None
          
    def get_tagged_users(self, obj):
        queryset = obj.tagged_users.all()
        userStruct = []
        for user in queryset:
            temp = {
                "id": user.id,
                "username": user.username,
            }
            userStruct.append(temp)
        return userStruct

    def get_note_attachment_id(self, obj):
        note_id = obj.id
        if not note_id:
            return []
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT azurefile_id FROM lsdb_note_attachments WHERE note_id = %s
            """, [note_id])
            return [row[0] for row in cursor.fetchall()] 


    class Meta:
        model = Note
        fields = [
            'id',
            'subject',
            'text',
            'datetime',
            'note_type_name',
            'author_name',
            'owner_name',
            'serial_number',
            'project_number',
            'test_sequence_name',
            'customer_name',
            'note_attachment_id',
            'tagged_users',
            'manufacturer',
            'bom',
            'module_model',
            'pmax',
            
        ]